vertical = function () {
        let upperCase = function (character) {
                let code = character.charCodeAt(0);
                if (code >= 97 && code <= 122)
                        return String.fromCharCode(code - 32);
                else
                        return character;
        };

        let input = Array.from(arguments).join(" ").split("").map(upperCase);
        if (input.length > 19)
                return "too long";
        else
                return input.join(" ") + "\n" + input.join("\n")
}
