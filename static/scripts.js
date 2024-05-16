let darko = false;
let buttontext = document.getElementById('dmtoggle');

function textswap() {
    var buttontext = document.getElementById('dmtoggle');
    if (buttontext.innerText == 'Dimmer') {
        buttontext.innerText = 'Brighter', darktime();
    } else {
        buttontext.innerText = 'Dimmer', darktime();
    }
}
function darktime() {
    console.log('darkness')
    darko = !darko
    if (darko) {
        document.body.classList.add('darkMode')
    } else {
        document.body.classList.remove('darkMode')
    }
    }
document.getElementById('dmtoggle').onclick = textswap