document.addEventListener('DOMContentLoaded', () => {
    
    // 信用卡號格式化 (自動加空格)
    const cardInput = document.getElementById('cardNumber');
    if (cardInput) {
        cardInput.addEventListener('input', (e) => {
            let value = e.target.value.replace(/\D/g, ''); // 移除所有非數字
            let formattedValue = '';
            for (let i = 0; i < value.length; i++) {
                if (i > 0 && i % 4 === 0) {
                    formattedValue += ' ';
                }
                formattedValue += value[i];
            }
            e.target.value = formattedValue;
        });
    }

    // 日期格式化 MM/YY
    const expiryInput = document.getElementById('expiry');
    if (expiryInput) {
        expiryInput.addEventListener('input', (e) => {
            let value = e.target.value.replace(/\D/g, '');
            if (value.length > 2) {
                value = value.substring(0, 2) + '/' + value.substring(2);
            }
            e.target.value = value;
        });
    }

    // 防詐騙 Modal 邏輯
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
                return;
            }
            modal.classList.add('active');
        });

        cancelBtn.addEventListener('click', () => {
            modal.classList.remove('active');
        });

        confirmPaymentBtn.addEventListener('click', () => {
            // 防止重複點擊
            confirmPaymentBtn.disabled = true;
            confirmPaymentBtn.innerText = '處理中...';
            paymentForm.submit();
        });

        // 點擊 Modal 外側不關閉，強迫使用者必須點擊按鈕，以符合防詐安全確認目的
    }
});
