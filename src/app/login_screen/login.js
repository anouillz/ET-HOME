// Petit JS si jamais c'est utile, permet de récupérer les champs dans username et password
document.getElementById('btn').addEventListener('click', function(event) {
    event.preventDefault();
    const username = document.getElementsByName('username')[0].value;
    const password = document.getElementsByName('password')[0].value;

    console.log(username);
    console.log(password);
});
