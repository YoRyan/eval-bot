bob = function () {
        let isLetter = function (character) {
                let code = character.charCodeAt(0);
                return (code >= 97 && code <= 122) || (code >= 65 && code <= 90);
        };
        let upperCase = function (character) {
                let code = character.charCodeAt(0);
                if (code >= 97 && code <= 122)
                        return String.fromCharCode(code - 32);
                else
                        return character;
        };
        let lowerCase = function (character) {
                let code = character.charCodeAt(0);
                if (code >= 65 && code <= 90)
                        return String.fromCharCode(code + 32);
                else
                        return character;
        };

        let theCase = "U";
        let results = [];
        for (let w = 0; w < arguments.length; w++) {
                let word = arguments[w];
                let result = "";
                for (let c = 0; c < word.length; c++) {
                        let char = word[c];
                        if (isLetter(char)) {
                                if (theCase === "U") {
                                        result += upperCase(char);
                                        theCase = "L";
                                } else if (theCase === "L") {
                                        result += lowerCase(char);
                                        theCase = "U";
                                }
                        } else {
                                result += char;
                        }
                }
                results.push(result);
        }
        return results.join(" ");
}
