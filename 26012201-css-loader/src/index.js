import * as css from './style.css';


// Add a div element to the body
const div = document.createElement('div');
div.classList.add('div');
div.textContent = 'Hello World!';
document.body.appendChild(div);

const exec = () => {
    console.log('hello world');
}

// Execute the function to ensure code is included in bundle
exec();

export default {
    exec,
};