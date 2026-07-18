#!/usr/bin/env python3
"""Juejin Publisher: login once, publish forever. Uses persistent browser profile."""
import subprocess, sys, os, json, time

JUEGIN_PROFILE = "/Users/mac/.juejin-browser-profile"
ARTICLE_DIR = "/Users/mac/Desktop/FlowWiki/ops/publishing/articles/v0.1.0-launch"
CONTENT_FILE = f"{ARTICLE_DIR}/juejin.md"
IMAGES = {
    "cover": f"{ARTICLE_DIR}/assets/cover.jpg",
    "arch": f"{ARTICLE_DIR}/assets/arch-diagram.jpg",
    "ace": f"{ARTICLE_DIR}/assets/ace-cycle.jpg",
    "compare": f"{ARTICLE_DIR}/assets/comparison.jpg",
}

def run_playwright(code):
    """Run Playwright code via CLI with persistent session."""
    with open("/tmp/juejin-pub-tmp.js", "w") as f:
        f.write(code)
    result = subprocess.run(
        ["playwright-cli", "-s=juejin-pub", "run-code", code],
        capture_output=True, text=True, timeout=60
    )
    return result.stdout.strip()

def is_logged_in():
    """Check if already logged in by visiting editor page."""
    code = '''async (page) => {
        await page.goto("https://juejin.cn/editor/drafts/new", { waitUntil: "networkidle" });
        await page.waitForTimeout(2000);
        const url = page.url();
        return url.includes("/editor/") ? "LOGGED_IN:" + url : "NOT_LOGGED_IN:" + url;
    }'''
    return run_playwright(code)

def login():
    """Open login page, wait for user to complete GitHub OAuth."""
    code = '''async (page) => {
        await page.goto("https://juejin.cn/login?to=https%3A%2F%2Fjuejin.cn%2Feditor%2Fdrafts%2Fnew", { waitUntil: "networkidle" });
        await page.waitForTimeout(3000);
        return "Login page opened. Please login in the browser window.";
    }'''
    print(run_playwright(code))
    print("请在浏览器窗口中完成 GitHub 登录...")

def publish_article():
    """Publish article with all content and images."""
    with open(CONTENT_FILE, 'r') as f:
        content = f.read()
    
    # Extract title (first line starting with #)
    title = content.split('\n')[0].replace('# ', '')
    
    # Build publish JS
    code = f'''async (page) => {{
        // Navigate to editor
        await page.goto("https://juejin.cn/editor/drafts/new", {{ waitUntil: "networkidle" }});
        await page.waitForTimeout(3000);
        
        const url = page.url();
        if (url.includes("/login")) {{
            return "ERROR: Not logged in. Run login first.";
        }}
        
        // Fill title
        const titleInput = await page.waitForSelector('input[placeholder*="输入文章标题"]');
        await titleInput.click();
        await titleInput.fill("");
        await titleInput.type({json.dumps(title)}, {{ delay: 10 }});
        await page.waitForTimeout(500);
        
        // Fill content via CodeMirror
        const cmExists = await page.evaluate(() => !!document.querySelector(".CodeMirror"));
        if (cmExists) {{
            await page.evaluate((c) => {{
                document.querySelector(".CodeMirror").CodeMirror.setValue(c);
            }}, {json.dumps(content)});
        }} else {{
            return "ERROR: CodeMirror not found";
        }}
        await page.waitForTimeout(1000);
        
        // Fill summary
        const summaryArea = await page.$("textarea.byte-input__textarea");
        if (summaryArea) {{
            const summary = "让知识像代码一样编译、缓存、复利增长。不是又一个 RAG，而是一个带防幻觉机制的 AI 知识库编译器。";
            await summaryArea.fill(summary);
        }}
        await page.waitForTimeout(500);
        
        // Click publish button to open dialog
        const publishBtn = await page.$("button:has-text('发布')");
        if (publishBtn) await publishBtn.click();
        await page.waitForTimeout(2000);
        
        // In publish popup: upload cover
        const coverInput = await page.$(".publish-popup input[type='file']");
        if (coverInput) {{
            await coverInput.setInputFiles({json.dumps(IMAGES['cover'])});
            await page.waitForTimeout(2000);
        }}
        
        // Set tag: 人工智能
        const tagInput = await page.$(".publish-popup .byte-select:first-child input");
        if (tagInput) {{
            await tagInput.click();
            await tagInput.fill("人工智能");
            await page.waitForTimeout(1500);
            // Click the dropdown option
            const tagOption = await page.$(".byte-select-dropdown .byte-option:first-child");
            if (tagOption) await tagOption.click();
            await page.waitForTimeout(500);
        }}
        
        return "Content filled. Ready to publish. Click '确定并发布' button.";
    }}'''
    return run_playwright(code)

if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "status"
    
    if cmd == "login":
        login()
    elif cmd == "publish":
        result = is_logged_in()
        if "NOT_LOGGED_IN" in result:
            print("Not logged in. Run login first.")
        else:
            print(publish_article())
    elif cmd == "status":
        result = is_logged_in()
        print(result)
    else:
        print(f"Usage: {sys.argv[0]} login|publish|status")
