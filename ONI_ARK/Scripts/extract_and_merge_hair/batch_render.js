const fs = require('fs');
const path = require('path');
const http = require('http');
const puppeteer = require('puppeteer');

// ================= 配置区 =================
// 设定你的目标总目录 (Windows 路径注意使用 String.raw 或双反斜杠)
const BASE_DIR = String.raw`D:\FD_Store\ARK_chara`;
// 用于提供本地 WebGL 渲染的临时端口
const PORT = 8080; 
// ==========================================

// 1. 递归查找所有 .skel 文件的函数 (已加入过滤逻辑)
function findSkelFiles(dir) {
    let results = [];
    const list = fs.readdirSync(dir);
    list.forEach(file => {
        const filePath = path.join(dir, file);
        
        // ==========================================
        // 【新增】：遇到基建相关的路径或文件，直接跳过！
        // 忽略所有路径中包含 'Building' 的文件夹，或者带有 'build_' 前缀的文件
        // ==========================================
        if (filePath.includes('Building') || file.startsWith('build_')) {
            return; 
        }

        const stat = fs.statSync(filePath);
        if (stat && stat.isDirectory()) {
            // 继续递归进入下一层文件夹
            results = results.concat(findSkelFiles(filePath));
        } else if (file.endsWith('.skel')) {
            // 找到符合条件的 skel 文件，存入列表
            results.push(filePath);
        }
    });
    return results;
}


// 2. 简易静态文件服务器 (解决 CORS 跨域和读取本地贴图的问题)
const server = http.createServer((req, res) => {
    const reqPath = decodeURI(req.url); // 解码 URL 路径
    const filePath = path.join(BASE_DIR, reqPath);
    if (fs.existsSync(filePath) && fs.statSync(filePath).isFile()) {
        res.setHeader('Access-Control-Allow-Origin', '*');
        res.writeHead(200);
        res.end(fs.readFileSync(filePath));
    } else {
        res.writeHead(404);
        res.end();
    }
});

(async () => {
    console.log(`[1] 正在扫描目录: ${BASE_DIR}`);
    if (!fs.existsSync(BASE_DIR)) {
        console.error("目录不存在，请检查路径！");
        process.exit(1);
    }
    
    const targetFiles = findSkelFiles(BASE_DIR);
    console.log(`✅ 共找到 ${targetFiles.length} 个 .skel 动画文件`);

    if (targetFiles.length === 0) process.exit(0);

    server.listen(PORT);
    console.log(`[2] 临时 HTTP 服务器已启动 (端口 ${PORT})`);

    console.log(`[3] 正在启动无头浏览器 (Puppeteer)...`);
    // 释放 GPU 性能，强制开启 WebGL 硬件加速
    const browser = await puppeteer.launch({ 
        // 在新版 Puppeteer 中，'new' 是调用新版无头模式。
        // 如果下面这套配置依然报错，请把这里的 'new' 改成 false（这会弹出一个真实的浏览器窗口自动狂刷，100% 能成功）
        headless: 'new', 
        args: [
            '--no-sandbox', 
            '--disable-setuid-sandbox', 
            '--ignore-gpu-blocklist', // 无视 Chrome 的 GPU 黑名单
            '--enable-webgl',         // 强制启用 WebGL 支持
            '--use-angle=default'     // 让底层的 ANGLE 引擎自动选择最优硬件接口
        ] 
    });
    const page = await browser.newPage();

    // 构建用来执行渲染的网页模板
    const htmlTemplate = `
        <!DOCTYPE html>
        <html>
        <head>
            <script src="https://unpkg.com/pixi.js@6.5.10/dist/browser/pixi.min.js"></script>
            <script src="https://unpkg.com/pixi-spine@2.1.11/dist/pixi-spine.js"></script>
        </head>
        <body>
            <script>
                async function renderSpine(skelUrl) {
                    return new Promise((resolve, reject) => {
                        const app = new PIXI.Application({ width: 1024, height: 1024, transparent: true });
                        document.body.appendChild(app.view);

                        // 每次使用独立的 Loader 防止批量加载时的命名冲突
                        const loader = new PIXI.Loader();
                        loader.add('model', skelUrl).load((_, resources) => {
                            if (!resources.model || !resources.model.spineData) {
                                resolve(null); return;
                            }
                            
                            const spineObj = new PIXI.spine.Spine(resources.model.spineData);
                            spineObj.x = 512;
                            spineObj.y = 612;
                            spineObj.scale.set(1.5);
                            spineObj.autoUpdate = false; // 冻结时间

                            try {
                                spineObj.state.setAnimation(0, 'Idle', false);
                            } catch (e) {
                                spineObj.state.setAnimation(0, spineObj.spineData.animations[0].name, false);
                            }
                            spineObj.update(0);

                            const keepKeywords = ['hair', 'braid', 'head', 'face', 'hat', 'horn', 'ear', 'ribbon', 'acc'];
                            // 【新增】：黑名单词库，把容易因为包含 ear, hat 等字母组合而误判的部位加进来
                            const excludeKeywords = ['forearm', 'spear', 'bear', 'gear', 'heart', 'wear', 'tear']; 

                            spineObj.skeleton.drawOrder.forEach((slot, zIndex) => {
                                const slotName = slot.data.name.toLowerCase();
                                
                                // 1. 是否命中了白名单？
                                const inWhitelist = keepKeywords.some(keyword => slotName.includes(keyword));
                                // 2. 是否不幸命中了黑名单？
                                const inBlacklist = excludeKeywords.some(keyword => slotName.includes(keyword));

                                // 【核心逻辑】：在白名单中，且绝对不在黑名单中，才准许保留
                                const shouldKeep = inWhitelist && !inBlacklist;

                                if (!shouldKeep) {
                                    slot.attachment = null;
                                    const originalIndex = slot.data.index;
                                    if (spineObj.slotContainers && spineObj.slotContainers[originalIndex]) {
                                        spineObj.slotContainers[originalIndex].visible = false;
                                        spineObj.slotContainers[originalIndex].renderable = false;
                                    }
                                }
                            });

                            app.stage.addChild(spineObj);
                            app.renderer.render(app.stage); // 强制渲染当前帧

                            // 提取画面
                            const canvas = app.renderer.plugins.extract.canvas(app.stage);
                            const base64 = canvas.toDataURL('image/png');
                            
                            // 彻底销毁实例释放内存，防止批量渲染 OOM
                            app.destroy(true, { children: true, texture: true, baseTexture: true });
                            
                            resolve(base64);
                        });
                    });
                }
            </script>
        </body>
        </html>
    `;

    // 将模板注入无头浏览器
    await page.setContent(htmlTemplate);

    console.log(`[4] 开始进行批量渲染和保存...`);
    
    // 开始遍历处理文件
    for (const filePath of targetFiles) {
        try {
            // 计算相对路径并转为 URL 格式
            const relativePath = path.relative(BASE_DIR, filePath).replace(/\\/g, '/');
            const fileUrl = `http://localhost:${PORT}/${encodeURI(relativePath)}`;
            
            // 【新增】：创建一个 5 秒的超时地雷
            const TIMEOUT_MS = 5000; 
            const timeoutPromise = new Promise((_, reject) => 
                setTimeout(() => reject(new Error(`卡住了！渲染超时 (${TIMEOUT_MS}ms)`)), TIMEOUT_MS)
            );

            // 【修改】：让正常渲染和超时地雷进行赛跑 (Promise.race)
            const base64Data = await Promise.race([
                page.evaluate(async (url) => {
                    return await renderSpine(url);
                }, fileUrl),
                timeoutPromise
            ]);

            if (!base64Data) {
                console.log(`⚠️ 跳过无效数据: ${relativePath}`);
                continue;
            }

            // 剥离 Base64 头部
            const base64Image = base64Data.split(';base64,').pop();
            
            // 构造输出路径：在原文件同级目录下生成同名 _hair.png
            const outputFileName = path.basename(filePath, '.skel') + '_hair.png';
            const outputDir = path.dirname(filePath);
            const outputPath = path.join(outputDir, outputFileName);

            // 写入本地磁盘
            fs.writeFileSync(outputPath, base64Image, { encoding: 'base64' });
            console.log(`📸 渲染成功: ${outputFileName}`);

        } catch (err) {
            console.error(`❌ 渲染失败 ${filePath}: \n`, err);
        }
    }

    console.log(`\n🎉 [5] 所有文件处理完毕！`);
    
    // 关闭服务退出
    await browser.close();
    server.close();
    process.exit(0);

})();