document.addEventListener("DOMContentLoaded", function () {
    // --- 1. 初始化粒子效果 (保持不变) ---
    if (window.particlesJS) {
        particlesJS("particles-js", {
            "particles": {
            "number": { "value": 80 },
            "size": { "value": 3 },
            "color": { "value": "#ffffff" }, // 白色粒子
            "line_linked": {
                "enable": true,
                "distance": 150,
                "color": "#ffffff",       // 白色连线
                "opacity": 0.6,
                "width": 1
            },
            "move": { "enable": true, "speed": 2 }
        }
        });
    }

    // --- 2. 最终的表单提交与判题逻辑 ---
    const form = document.getElementById("interaction-form");
    const submitButton = document.getElementById("submit-button");
    const resultContainer = document.getElementById("judge-result-container");

    if (form) {
        form.addEventListener("submit", async function (event) {
            // 阻止表单的默认跳转行为
            event.preventDefault();

            // a. 获取所有输入框的值
            const nickname = document.getElementById("nickname").value;
            const email = document.getElementById("email").value;
            const code = document.getElementById("code-submission").value;
            
            // b. 提供即时反馈：禁用按钮并显示加载状态
            submitButton.disabled = true;
            submitButton.textContent = '正在运行...';
            resultContainer.innerHTML = '<p class="result-warning">判题中...</p>';

            // c. 定义后端 API 地址
            const apiUrl = 'http://127.0.0.1:8000/api/judge';

            try {
                // d. 发起 fetch POST 请求
                const response = await fetch(apiUrl, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        nickname: nickname,
                        email: email,
                        code: code
                    }),
                });

                // 如果服务器返回非 2xx 的状态码，则抛出错误
                if (!response.ok) {
                    const errorData = await response.json();
                    throw new Error(`服务器错误: ${response.status} - ${errorData.detail || '未知错误'}`);
                }

                const result = await response.json();
                
                // e. 根据后端返回的结果，更新 UI
                let resultClass = '';
                switch (result.status) {
                    case 'Accept':
                        resultClass = 'result-accept';
                        break;
                    case 'Wrong Answer':
                    case 'System Error':
                        resultClass = 'result-error';
                        break;
                    // 为未来的 Compile Error 状态做准备
                    case 'Runtime Error':
                        resultClass = 'result-warning';
                        break;
                    default:
                        resultClass = 'result-warning';
                }

                // 将格式化的结果显示在页面上
                // 使用 <pre> 标签可以保留错误信息的格式（如换行）
                if (result.status === 'Accept' || result.status === 'Wrong Answer') {
                resultContainer.innerHTML = `
                    <p class="${resultClass}"><strong>${result.status}!</strong></p>
                `;
                }
                else {
                resultContainer.innerHTML = `
                    <p class="${resultClass}"><strong>${result.status}</strong></p>
                    <pre class="${resultClass}">${result.message}</pre>
                `;
                }

            } catch (error) {
                // f. 处理网络错误或服务器错误
                console.error('提交或判题失败:', error);
                resultContainer.innerHTML = `
                    <p class="result-error"><strong>请求失败</strong></p>
                    <pre class="result-error">${error.message}</pre>
                `;
            } finally {
                // g. 无论成功与否，最后都恢复按钮状态
                submitButton.disabled = false;
                submitButton.textContent = '提交代码并运行测试';
            }
        });
    }
});
