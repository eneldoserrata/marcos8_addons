//Get all the keys from document
var keys = document.querySelectorAll('#calculator span');
var operators = ['+', '-', 'x', '/'];
var dCount = false;
var justEvaled = false;

//Add onclick event to all the keys and perform operations
for(var i = 0; i < keys.length; i++) {
	keys[i].onclick = function(e) {
		//Get the input and button values
		var input = document.querySelector('.screen');
		var inputVal = input.innerHTML;
		var btnVal = this.innerHTML;

		//Now, just append the key values (btnValue) to the input
		//string and finally use javascript's eval function to the
		//result
		//If clear key is pressed, erase everything
		if (btnVal == 'C') {
			input.innerHTML = "";
		}

		//If eval key is pressed, calculate and display the result
		else if (btnVal == '=') {
			var equation = inputVal;
			var lastChar = equation[equation.length - 1];

			//Replace all instances of x and ÷ with * and / respectively.
			//This can be done easily using regex and and the 'g' tag
			//which will replace all instances of the matched character
			equation = equation.replace(/x/g, '*')

			//If the final character is an operator or decimal point remove
			//it before evaluating
			if (operators.indexOf(lastChar) > -1 || lastChar == '.'){
				equation = equation.replace(/.$/, "");
			}

			if (equation) {
				input.innerHTML = eval(equation);
			}
			dCount = false;
			justEvaled = true;
		}

		// Basic functionality of the calculator is complete. 
		//But there are some problems like 
		//1. No two operators should be added consecutively.
		//2. The equation shouldn't start from an operator except minus
		//3. not more than 1 decimal should be there in a number

		// We'll fix these issues using some simple checks
		//indexOf works only in IE9+
		else if (operators.indexOf(btnVal) > -1) {
			//Operator is clicked
			//Get the last character from the equation
			var lastChar = inputVal[inputVal.length - 1];

			if (justEvaled) {
				input.innerHTML = ""
				justEvaled = false;
			}

			//Only add operator if input is not empty and there is no
			//operator at the last index
			if (inputVal != "" && operators.indexOf(lastChar) == -1) {
				input.innerHTML += btnVal;
			}

			//Allow minus if the string is empty
			else if (inputVal == "" && btnVal == "-") {
				input.innerHTML += btnVal;
			}

			//Replace the last operator (if exists) with the newly
			//pressed operator
			else if (operators.indexOf(lastChar) > -1 && inputVal.length > 1) {
				input.innerHTML = inputVal.replace(/.$/, btnVal);
			}
			dCount = false;
		}

		//Now the decimals... we'll use a variable, dCount to keep track
		//of how whether a decimal has been added already and reset it
		//when an operator is inserted
		else if (btnVal == ".") {
			if (!dCount) {
				dCount = true;
				input.innerHTML += btnVal;
			}
		}

		//If any other key is pressed, just append it
		else {
			if (justEvaled) {
				//Added functionality
				//If you just completed an operation, when you click on
				//another button to start a new operation it will autoclear
				input.innerHTML = ""
				justEvaled = false;
			}
			input.innerHTML += btnVal;
		}

		//prevent page jumps
		e.preventDefault();
	}
}