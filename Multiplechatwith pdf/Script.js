// Backend URL
const backendUrl = 'http://127.0.0.1:5000'; // Ensure this matches your Flask backend URL

let userEmail = '';

// Handle Registration
document.getElementById('register-form').addEventListener('submit', async function (e) {
    e.preventDefault();
    const email = document.getElementById('register-email').value;
    const password = document.getElementById('register-password').value;

    const response = await fetch(`${backendUrl}/register`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password })
    });
    const result = await response.json();
    if (result.status === 'success') {
        alert('Registration successful. Please login.');
        document.getElementById('register-page').style.display = 'none';
        document.getElementById('login-page').style.display = 'block';
    } else {
        alert(result.message);
    }
});

// Handle Login
document.getElementById('login-form').addEventListener('submit', async function (e) {
    e.preventDefault();
    const email = document.getElementById('login-email').value;
    const password = document.getElementById('login-password').value;

    const response = await fetch(`${backendUrl}/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password })
    });
    const result = await response.json();
    if (result.status === 'success') {
        userEmail = email;
        document.getElementById('login-page').style.display = 'none';
        document.getElementById('chat-page').style.display = 'block';
    } else {
        alert(result.message);
    }
});

// Handle Document Upload and Processing
document.getElementById('process-docs-btn').addEventListener('click', async function () {
    const documentsInput = document.getElementById('documents-input');
    const files = documentsInput.files;

    if (files.length === 0) {
        alert('Please select at least one document.');
        return;
    }

    const formData = new FormData();
    formData.append('email', userEmail);
    for (const file of files) {
        formData.append('documents', file);
    }

    const response = await fetch(`${backendUrl}/process_documents`, {
        method: 'POST',
        body: formData
    });
    const result = await response.json();
    if (result.status === 'success') {
        alert('Documents processed successfully.');
    } else {
        alert(result.message);
    }
});

// Chat functionality
document.getElementById('send-btn').addEventListener('click', async function () {
    const userInput = document.getElementById('user-input').value;
    if (userInput.trim() === '') return;

    // Append user message
    const userMessage = document.createElement('div');
    userMessage.classList.add('message', 'user-message');
    userMessage.textContent = userInput;
    document.getElementById('chat-box').appendChild(userMessage);

    // Scroll to bottom
    document.getElementById('chat-box').scrollTop = document.getElementById('chat-box').scrollHeight;

    // Clear input field
    document.getElementById('user-input').value = '';

    // Send message to backend
    const response = await fetch(`${backendUrl}/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email: userEmail, message: userInput })
    });
    const result = await response.json();

    // Append bot response
    const botMessage = document.createElement('div');
    botMessage.classList.add('message', 'bot-message');
    botMessage.textContent = result.response;
    document.getElementById('chat-box').appendChild(botMessage);

    // Scroll to bottom
    document.getElementById('chat-box').scrollTop = document.getElementById('chat-box').scrollHeight;
});

// Logout functionality
document.getElementById('logout').addEventListener('click', function () {
    userEmail = '';
    document.getElementById('chat-page').style.display = 'none';
    document.getElementById('login-page').style.display = 'block';
});
