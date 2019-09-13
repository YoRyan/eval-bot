murica = function () {
        let value = parseFloat(arguments[0]);
        let unit = arguments[1];
        if (unit === "km")
                value *= 1000;
        else if (unit === "cm")
                value *= .01;
        else if (unit === "mm")
                value *= .001;
        else if (unit !== "m")
                return "Unknown unit";

        let round = function (value) {
                return value.toFixed(2);
        };
        if (value < 0.3048)
                return round(value*39.3701) + " in";
        else if (value < 402.336)
                return round(value*3.28084) + " ft";
        else
                return round(value*.000621371) + " mi";
}
