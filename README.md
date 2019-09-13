# Eval Bot

...is a Discord but that runs programmable JavaScript snippets on your server.

Traditionally, a custom Discord bot is an intense development effort involving
multiple collaborating programmers and a dedicated Github repository. Eval Bot
takes a different approach by giving server members the ability to define their
own commands using JavaScript, a language that is popular and familiar even to
programming novices. Setup takes place entirely through Discord, allowing you to
focus on writing fun and creative snippets instead of tiresome boilerplate code.

## Add to Discord

I run a copy of the bot 24/7, and you can add it to your Discord server by
following this [invite link](https://discordapp.com/api/oauth2/authorize?client_id=621193444613947414&permissions=2048&scope=bot).

## Manual

```
-- General --
help    : Show this help
prefix  : Change this bot's command prefix
role    : Set a required role to manage commands
set     : Add or update a custom command
sethelp : Add help text for a custom command
remove  : Remove a custom command
show    : Retrieve the JavaScript source of a command
```

### Your first command

By default, all commands are prefixed with `!`. As a server operator, you may
change this if it conflict with another bot.

TODO

### Code samples

Eval Bot scales to a variety of uses, from a simple communal bookmark tool to
calculators to automated meme-making.

Make fun of Reddit:

```
return "You committed the ultimate cardinal sin, you got personal. You, as a team of professionals trying to make money, got personal."
```

Dice roll:

```
return [1,2,3,4,5,6][Math.floor(Math.random()*6]
```

LMGTFY:

```
return "https://lmgtfy.com/?q="+arguments.join("+")
```

My personal favorite, MaKe SpOnGeBoB mEmE tExT:

```
let t=function(t){let e=t.charCodeAt(0);return e>=97&&e<=122||e>=65&&e<=90},e=function(t){let e=t.charCodeAt(0);return e>=97&&e<=122?String.fromCharCode(e-32):t},r=function(t){let e=t.charCodeAt(0);return e>=65&&e<=90?String.fromCharCode(e+32):t},n="U",o=[];for(let l=0;l<arguments.length;l++){let u=arguments[l],f="";for(let o=0;o<u.length;o++){let l=u[o];t(l)?"U"===n?(f+=e(l),n="L"):"L"===n&&(f+=r(l),n="U"):f+=l}o.push(f)}return o.join(" ")
```

### JavaScript programming guide

Eval Bot uses [Python Mini Racer](https://github.com/sqreen/PyMiniRacer) to
interpret JavaScript code, which includes the standard library (`Math`, `String`,
etc.).

Currently, snippets have the following limitations:

- Code must fit within the 2000-character limit of a single Discord message
- No persistent storage
- No ability to retrieve Internet resources
- No ability to interact with Discord data
- Cannot call other snippets
- Must not exceed 10 seconds of runtime, or 50 MB of memory usage (on the public
  bot)

Internally, JavaScript commands are represented as functions
(`<name> = function () { ... }`), and your job as a snippet writer is simply to
fill in the body. When your function is called on Discord, all arguments--
specifically, all whitespace-separated words--are passed to your function in the
form of a variable-length list of strings.

Thus,

```
!say hello world!
```

becomes

```
say("hello", "world!")
```

You can access these arguments using the JavaScript-standard (and appropriately
named) `arguments` array.

In short, to produce a snippet, simply write a standalone JavaScript function,
then [minify it](https://javascript-minifier.com), and finally strip the
function declaration.
