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
!help        : Show this help
!evalprefix  : Change this bot's command prefix
!role        : Set a required role to manage commands
!set         : Add or update a custom command
!sethelp     : Add help text for a custom command
!remove      : Remove a custom command
!show        : Retrieve the JavaScript source of a command
```

### Your first command

Out of the box, all commands are prefixed with `!`. As a server operator, you
can change this if it conflicts with another bot.

The `set` command creates (or updates) commands:

```
!set <command name> <JavaScript source>

!set hello return "Hello, World!"
```

To get a list of all custom commands on your server, use the `help` command,
which lists custom commands alongside Eval Bot's standard commands:

```
-- General --
!help       : Show this help
(...)

-- This Server --
!hello      : (no help text set)
```

The help text of a custom command can (optionally) be set by the `sethelp`
command.

```
!sethelp <command name> <help text>

!sethelp hello Run my very first command
```

Finally, for security and anti-griefing purposes, you can set a role that server
members need to manage commands. This is done with the `role` command:

```
!role <the role>

!role Cool Kids
```

### Code samples

Eval Bot scales to a variety of uses, from simple community bookmarks to
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

MaKe SpOnGeBoB mEmE tExT (the genesis of this project!):

```
let t=function(t){let e=t.charCodeAt(0);return e>=97&&e<=122||e>=65&&e<=90},e=function(t){let e=t.charCodeAt(0);return e>=97&&e<=122?String.fromCharCode(e-32):t},r=function(t){let e=t.charCodeAt(0);return e>=65&&e<=90?String.fromCharCode(e+32):t},n="U",o=[];for(let l=0;l<arguments.length;l++){let u=arguments[l],f="";for(let o=0;o<u.length;o++){let l=u[o];t(l)?"U"===n?(f+=e(l),n="L"):"L"===n&&(f+=r(l),n="U"):f+=l}o.push(f)}return o.join(" ")
```

### JavaScript programming guide

Eval Bot uses [Python Mini Racer](https://github.com/sqreen/PyMiniRacer) to
interpret JavaScript code, which includes the standard library (`Math`, `String`,
etc.) and ECMAScript 6 features.

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
fill in the body. When your function is called on Discord, all
arguments--specifically, all whitespace-separated words--are passed to your
function in the form of a variable-length list of strings.

Thus, the Discord message

```
!say hello world!
```

is translated to JavaScript code as

```
say("hello", "world!")
```

You can access these arguments using the JavaScript-standard (and appropriately
named) `arguments` array.

In short, to produce a snippet:

1. Write a standalone JavaScript function.
2. [Minify it](https://javascript-minifier.com) to compress its source code.
3. Strip the function declaration and feed the function body to the `set`
   command.
