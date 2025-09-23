if (document.getElementById('register-form')) {
    document.getElementById('register-form').onsubmit = async function (e) {
        e.preventDefault();
        let username = document.getElementById('username').value.trim();
        let password = document.getElementById('password').value;
        let res = await fetch('/api/register', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, password })
        });
        let data = await res.json();
        let msgDiv = document.getElementById('msg');
        msgDiv.innerText = data.msg;
        msgDiv.style.color = data.success ? "green" : "red";
    }
}
