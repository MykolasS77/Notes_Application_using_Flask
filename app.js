let token = '';

function register() {
    const username = document.getElementById('register-username').value;
    const password = document.getElementById('register-password').value;

    fetch('/register', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({username, password})
    })
    .then(res => res.json())
    .then(data => alert(data.message));
}

function login() {
    const username = document.getElementById('login-username').value;
    const password = document.getElementById('login-password').value;

    fetch('/login', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({username, password})
    })
    .then(res => res.json())
    .then(data => {
        if (data.access_token) {
            token = data.access_token;
            alert('Login successful!');
        } else {
            alert('Login failed!');
        }
    });
}

function getNotes() {
    fetch('/notes', {
        headers: {'Authorization': 'Bearer ' + token}
    })
    .then(res => res.json())
    .then(data => {
        const list = document.getElementById('notes-list');
        list.innerHTML = '';
        data.forEach(note => {
            const li = document.createElement('li');
            li.innerText = `${note.title}: ${note.content}`;
            list.appendChild(li);
        });
    });
}
