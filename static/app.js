let token = '';

function register() {
    const username = document.getElementById('register-username').value;
    const password = document.getElementById('register-password').value;

    fetch('/register', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({username, password})
    })
    .then(async res => {
        const data = await res.json();
        if (res.ok) {
            alert(data.message); // "User registered successfully!"
        } else {
            alert(data.message); // "User already exists!" or error
        }
    });
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
            // Show the welcome section after successful login
            document.getElementById('welcome-section').style.display = 'block';
            document.getElementById('welcome-message').innerText = `Welcome, ${username}!`;
            // Load existing notes
            getNotes();
            alert('Login successful!');
        } else {
            alert('Login failed!');
        }
    });
}

function getNotes() {
    console.log('Token being sent:', token); // Debug log
    fetch('/notes', {
        headers: {'Authorization': 'Bearer ' + token}
    })
    .then(res => {
        console.log('Response status:', res.status); // Debug log
        if (res.ok) {
            return res.json();
        } else {
            throw new Error(`HTTP error! status: ${res.status}`);
        }
    })
    .then(data => {
        const list = document.getElementById('notes-list');
        list.innerHTML = '';
        data.forEach(note => {
            const li = document.createElement('li');
            li.innerText = `${note.title}: ${note.content}`;
            list.appendChild(li);
        });
    })
    .catch(error => {
        console.error('Error getting notes:', error);
        // Try to get more detailed error information
        if (error.message) {
            console.error('Error message:', error.message);
        }
    });
}

function addNote() {
    const title = document.getElementById('note-title').value;
    const content = document.getElementById('note-content').value;

    if (!title || !content) {
        alert('Please enter both title and content');
        return;
    }

    console.log('Adding note with token:', token); // Debug log
    fetch('/notes', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer ' + token
        },
        body: JSON.stringify({title, content})
    })
    .then(res => {
        if (res.ok) {
            return res.json();
        } else {
            throw new Error(`HTTP error! status: ${res.status}`);
        }
    })
    .then(data => {
        // Clear the input fields
        document.getElementById('note-title').value = '';
        document.getElementById('note-content').value = '';
        // Refresh the notes list
        getNotes();
        alert('Note added successfully!');
    })
    .catch(error => {
        console.error('Error adding note:', error);
        console.error('Error details:', error.message);
        // Try to get response text for more details
        alert('Error adding note: ' + error.message);
    });
}
