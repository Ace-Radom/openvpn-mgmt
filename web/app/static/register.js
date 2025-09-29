const REGEX_USERNAME = /^[A-Z][a-z]*$/;
const REGEX_EMAIL = /^\S+@\S+\.\S+$/;
const REGEX_PSWD = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)[^\s]{6,}$/;

async function loadSVG(url) {
    const res = await fetch(url);
    return await res.text();
}

let iconCheck = null;
let iconCross = null;
let iconLoaded = false;
Promise.all([
    loadSVG('/static/icons/check.svg').then(svg => iconCheck = svg),
    loadSVG('/static/icons/cross.svg').then(svg => iconCross = svg)
]).then(() => {
    iconLoaded = true;
});

function validateUsername(username) {
    return REGEX_USERNAME.test(username);
}

function validateEmail(email) {
    return REGEX_EMAIL.test(email);
}

function validatePswd(pswd) {
    return REGEX_PSWD.test(pswd);
}

function validatePswdConfirm(pswd, pswd2) {
    return pswd === pswd2 && REGEX_PSWD.test(pswd);
}

function setIcon(element, valid) {
    if (!iconLoaded) {
        return;
    }

    if (valid === null) {
        element.innerHTML = '';
        element.className = 'input-icon';
        return;
    }
    element.innerHTML = valid ? iconCheck : iconCross;
    element.className = 'input-icon ' + (valid ? 'valid' : 'invalid');
    return;
}

if (document.getElementById('register-form')) {

    const usernameInput = document.getElementById('username');
    const usernameIcon = document.getElementById('username_icon');
    const emailInput = document.getElementById('email');
    const emailIcon = document.getElementById('email_icon');
    const pswdInput = document.getElementById('password');
    const pswdIcon = document.getElementById('password_icon');
    const pswd2Input = document.getElementById('password_confirm');
    const pswd2Icon = document.getElementById('password_confirm_icon');

    usernameInput.addEventListener('input', function () {
        if (!usernameInput.value) {
            setIcon(usernameIcon, null);
        }
        else {
            setIcon(usernameIcon, validateUsername(usernameInput.value));
        }
    });

    emailInput.addEventListener('input', function () {
        if (!emailInput.value) {
            setIcon(emailIcon, null);
        }
        else {
            setIcon(emailIcon, validateEmail(emailInput.value));
        }
    });

    pswdInput.addEventListener('input', function () {
        if (!pswdInput.value) {
            setIcon(pswdIcon, null);
        }
        else {
            setIcon(pswdIcon, validatePswd(pswdInput.value));
        }
    });

    pswd2Input.addEventListener('input', function () {
        if (!pswd2Input.value) {
            setIcon(pswd2Icon, null);
        }
        else {
            setIcon(pswd2Icon, validatePswdConfirm(pswdInput.value, pswd2Input.value));
        }
    });

    document.getElementById('register-form').onsubmit = async function (e) {
        e.preventDefault();
        let msg = document.getElementById('msg');

        let username = document.getElementById('username').value;
        let email = document.getElementById('email').value;
        let pswd = document.getElementById('password').value;
        let pswd2 = document.getElementById('password_confirm').value;

        if (!validateUsername(username)) {
            msg.style.color = 'red';
            msg.innerHTML = '无效用户名。';
        } else if (!validateEmail(email)) {
            msg.style.color = 'red';
            msg.innerHTML = '无效邮箱地址。';
        } else if (!validatePswd(pswd)) {
            msg.style.color = 'red';
            msg.innerHTML = '无效密码。';
        } else if (!validatePswdConfirm(pswd, pswd2)) {
            msg.style.color = 'red';
            msg.innerHTML = '两次输入的密码不一致。';
        } else {
            msg.style.color = 'green';
            msg.innerHTML = '';
        }

        if (msg.innerHTML) {
            return;
        }

        let res = await fetch('/api/register', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, password: pswd, email })
        });
        let data = await res.json();
        msg.innerText = data.msg;
        msg.style.color = data.success ? "green" : "red";
        if (data.success) {
            window.location.href = `/success?msg=注册成功！&next=/login`;
        }
    }
}
