document.addEventListener('DOMContentLoaded', () => {

    // ===== 信用卡號格式化 (自動加空格) =====
    const cardInput = document.getElementById('cardNumber');
    if (cardInput) {
        cardInput.addEventListener('input', (e) => {
            let value = e.target.value.replace(/\D/g, '');
            let formatted = value.match(/.{1,4}/g)?.join(' ') || '';
            e.target.value = formatted;
        });
    }

    // ===== 有效期限格式化 MM/YY =====
    const expiryInput = document.getElementById('expiry');
    if (expiryInput) {
        expiryInput.addEventListener('input', (e) => {
            let value = e.target.value.replace(/\D/g, '');
            if (value.length > 2) {
                value = value.substring(0, 2) + '/' + value.substring(2, 4);
            }
            e.target.value = value;
        });
    }

    // ===== CVC 僅允許數字 =====
    const cvcInput = document.getElementById('cvc');
    if (cvcInput) {
        cvcInput.addEventListener('input', (e) => {
            e.target.value = e.target.value.replace(/\D/g, '').substring(0, 3);
        });
    }

    // ===== Radio 付款方式切換樣式 =====
    const radioButtons = document.querySelectorAll('.radio-btn');
    radioButtons.forEach(btn => {
        const input = btn.querySelector('input[type="radio"]');
        if (input) {
            input.addEventListener('change', () => {
                radioButtons.forEach(b => b.classList.remove('active'));
                if (input.checked) btn.classList.add('active');
            });
        }
    });

    // ===== 防詐騙 Modal 邏輯 =====
    const initiatePaymentBtn = document.getElementById('initiatePaymentBtn');
    const modal = document.getElementById('antiScamModal');
    const cancelBtn = document.getElementById('cancelBtn');
    const confirmPaymentBtn = document.getElementById('confirmPaymentBtn');
    const paymentForm = document.getElementById('paymentForm');

    if (initiatePaymentBtn && modal) {
        initiatePaymentBtn.addEventListener('click', () => {
            // 基礎表單驗證
            if (!paymentForm.checkValidity()) {
                paymentForm.reportValidity();
                // 震動效果提示
                paymentForm.querySelectorAll('.input-field:invalid').forEach(el => {
                    el.style.borderColor = 'var(--danger)';
                    el.style.boxShadow = '0 0 0 3px rgba(244, 63, 94, 0.2)';
                    setTimeout(() => {
                        el.style.borderColor = '';
                        el.style.boxShadow = '';
                    }, 2000);
                });
                return;
            }
            modal.classList.add('active');
        });

        cancelBtn.addEventListener('click', () => {
            modal.classList.remove('active');
        });

        confirmPaymentBtn.addEventListener('click', () => {
            // 防止重複點擊，顯示 loading 狀態
            confirmPaymentBtn.disabled = true;
            confirmPaymentBtn.classList.add('loading');
            confirmPaymentBtn.innerText = '  處理中...';
            paymentForm.submit();
        });

        // 點擊 Modal 外側不關閉 — 強迫使用者必須點按鈕（防詐安全設計）
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                // 輕微搖晃提示不可關閉
                modal.querySelector('.modal-content').style.animation = 'none';
                void modal.querySelector('.modal-content').offsetWidth;
                modal.querySelector('.modal-content').style.animation = 'shake 0.4s ease';
            }
        });
    }

    // ===== Flash message 自動淡出 =====
    const flashMessages = document.querySelectorAll('.alert');
    flashMessages.forEach(msg => {
        setTimeout(() => {
            msg.style.transition = 'opacity 0.5s, transform 0.5s';
            msg.style.opacity = '0';
            msg.style.transform = 'translateY(-8px)';
            setTimeout(() => msg.remove(), 500);
        }, 4000);
    });

    // ===== 表格行 hover 動畫 =====
    const tableRows = document.querySelectorAll('.history-table tbody tr');
    tableRows.forEach((row, i) => {
        row.style.animationDelay = `${i * 0.05}s`;
        row.style.animation = 'fadeInRow 0.4s ease both';
    });

    // ===== 數字計數動畫（金額顯示） =====
    const amountEl = document.querySelector('.amount');
    if (amountEl) {
        const text = amountEl.textContent;
        const match = text.match(/[\d,]+/);
        if (match) {
            const target = parseInt(match[0].replace(/,/g, ''));
            const prefix = text.split(match[0])[0];
            const suffix = text.split(match[0])[1] || '';
            let current = 0;
            const duration = 1000;
            const steps = 40;
            const increment = target / steps;
            const interval = duration / steps;
            const counter = setInterval(() => {
                current = Math.min(current + increment, target);
                amountEl.textContent = prefix + Math.floor(current).toLocaleString() + suffix;
                if (current >= target) clearInterval(counter);
            }, interval);
        }
    }
});

// ===== Shake 動畫（Modal 無法關閉提示） =====
const shakeStyle = document.createElement('style');
shakeStyle.textContent = `
    @keyframes shake {
        0%, 100% { transform: translateX(0); }
        20% { transform: translateX(-8px); }
        40% { transform: translateX(8px); }
        60% { transform: translateX(-5px); }
        80% { transform: translateX(5px); }
    }
    @keyframes fadeInRow {
        from { opacity: 0; transform: translateY(8px); }
        to { opacity: 1; transform: translateY(0); }
    }
`;
document.head.appendChild(shakeStyle);
