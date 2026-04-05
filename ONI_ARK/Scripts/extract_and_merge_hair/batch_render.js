const fs = require('fs');
const path = require('path');
const http = require('http');
const puppeteer = require('puppeteer');

const BASE_DIR = String.raw`D:\FD_Store\ARK_chara`;
const PORT = 8080;

// ================= 部位配置表 =================
const PARTS_CONFIG = {
    "headshape": {
        keep: ['hair', 'braid', 'head', 'face', 'hat', 'horn', 'ear', 'ribbon', 'acc'],
        exclude: ['forearm', 'spear', 'bear', 'gear', 'heart', 'wear', 'tear']
    },
    "mouth": { keep: ['mouth', 'lip'], exclude: [] },
    "eyes": { keep: ['eye'], exclude: [] },
    "belt": { keep: ['belt'], exclude: [] },
    "neck": { keep: ['neck', 'collar'], exclude: [] },
    "cuff": { keep: ['cuff', 'wrist'], exclude: [] },
    "foot": { keep: ['foot', 'shoe', 'toe'], exclude: [], side: 'l' },
    "hand": { keep: ['hand', 'palm', 'finger'], exclude: [], side: 'l' }, // 只搜L
    "pelvis": { keep: ['pelvis', 'hip', 'crotch', 'waist'], exclude: ['belt'] },
    "leg": { keep: ['leg', 'thigh', 'shin', 'knee'], exclude: [], side: 'l' } // 只搜L
};

// 忽略列表（直接生成透明图）
const EMPTY_PARTS = ['hair', 'hat_hair'];

// =============================================

function findSkelFiles(dir) {
    let results = [];
    if (!fs.existsSync(dir)) return results;
    const list = fs.readdirSync(dir);
    list.forEach(file => {
        const filePath = path.join(dir, file);
        if (filePath.includes('Building') || file.startsWith('build_')) return;
        const stat = fs.statSync(filePath);
        if (stat && stat.isDirectory()) {
            results = results.concat(findSkelFiles(filePath));
        } else if (file.endsWith('.skel')) {
            results.push(filePath);
        }
    });
    return results;
}

const server = http.createServer((req, res) => {
    const reqPath = decodeURI(req.url);
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
    const targetFiles = findSkelFiles(BASE_DIR);
    server.listen(PORT);

    const browser = await puppeteer.launch({
        headless: 'new',
        args: ['--no-sandbox', '--disable-setuid-sandbox', '--ignore-gpu-blocklist', '--enable-webgl']
    });
    const page = await browser.newPage();

    // 构建支持多部位渲染的 HTML
    const htmlTemplate = `
        <!DOCTYPE html>
        <html>
        <head>
            <script src="https://unpkg.com/pixi.js@6.5.10/dist/browser/pixi.min.js"></script>
            <script src="https://unpkg.com/pixi-spine@2.1.11/dist/pixi-spine.js"></script>
        </head>
        <body>
            <script>
                const app = new PIXI.Application({ width: 1024, height: 1024, transparent: true });
                document.body.appendChild(app.view);
                let currentSpine = null;

                async function loadModel(url) {
                    if (currentSpine) { app.stage.removeChild(currentSpine); currentSpine.destroy(); }
                    return new Promise(resolve => {
                        const loader = new PIXI.Loader();
                        loader.add('model', url).load((_, res) => {
                            currentSpine = new PIXI.spine.Spine(res.model.spineData);
                            currentSpine.x = 512; currentSpine.y = 800; // 默认位置
                            currentSpine.autoUpdate = false;
                            try {
                                const anim = currentSpine.spineData.animations.find(a => a.name === 'Idle') || currentSpine.spineData.animations[0];
                                currentSpine.state.setAnimation(0, anim.name, false);
                            } catch(e){}
                            currentSpine.update(0);
                            app.stage.addChild(currentSpine);
                            resolve(true);
                        });
                    });
                }

                function renderPart(config) {
                    let foundAny = false;
                    currentSpine.skeleton.slots.forEach((slot, i) => {
                        const name = slot.data.name.toLowerCase();
                        // 逻辑：白名单 AND 不在黑名单 AND (如果不分左右 OR 匹配到侧边)
                        const isWhite = config.keep.some(k => name.includes(k));
                        const isBlack = config.exclude.some(k => name.includes(k));
                        const isSideOk = !config.side || name.includes('_' + config.side + '_');
                        
                        const visible = isWhite && !isBlack && isSideOk;
                        if (visible) foundAny = true;

                        slot.attachment = visible ? slot.data.attachmentName : null;
                        if (currentSpine.slotContainers[i]) {
                            currentSpine.slotContainers[i].visible = visible;
                        }
                    });

                    if (!foundAny) return "EMPTY";
                    
                    app.renderer.render(app.stage);
                    return app.renderer.plugins.extract.canvas(app.stage).toDataURL('image/png');
                }
            </script>
        </body>
        </html>
    `;

    await page.setContent(htmlTemplate);

    for (const filePath of targetFiles) {
        try {
            const relPath = path.relative(BASE_DIR, filePath).replace(/\\/g, '/');
            const fileUrl = `http://localhost:${PORT}/${encodeURI(relPath)}`;

            // 1. 创建存放部件的文件夹
            const parentFolderName = path.basename(path.dirname(filePath));
            const outputDir = path.join(path.dirname(filePath), `${parentFolderName}_extracted_parts`);
            if (!fs.existsSync(outputDir)) fs.mkdirSync(outputDir);

            console.log(`\n📦 正在处理干员: ${parentFolderName}`);

            // 加载模型
            await page.evaluate(async (url) => await loadModel(url), fileUrl);

            // 2. 渲染实际存在的部位
            for (const [partName, config] of Object.entries(PARTS_CONFIG)) {
                const base64Data = await page.evaluate((cfg) => renderPart(cfg), config);
                const outPath = path.join(outputDir, `${partName}.png`);

                if (base64Data === "EMPTY") {
                    // 生成 1x1 透明图
                    fs.writeFileSync(outPath, "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNkYAAAAAYAAjCB0C8AAAAASUVORK5CYII=", 'base64');
                } else {
                    fs.writeFileSync(outPath, base64Data.split(',')[1], 'base64');
                }
                process.stdout.write(`[${partName}] `);
            }

            // 3. 渲染预设为空的部位
            for (const partName of EMPTY_PARTS) {
                const outPath = path.join(outputDir, `${partName}.png`);
                fs.writeFileSync(outPath, "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNkYAAAAAYAAjCB0C8AAAAASUVORK5CYII=", 'base64');
                process.stdout.write(`[${partName}(skip)] `);
            }

        } catch (err) {
            console.error(`\n❌ 出错 ${filePath}: ${err.message}`);
        }
    }

    console.log(`\n\n🎉 全部完成！`);
    await browser.close();
    server.close();
})();