#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""A programmable JavaScript bot for Discord."""

import logging
import sqlite3
import sys

import discord
from py_mini_racer import py_mini_racer


__author__ = 'Ryan Young'
__version__ = '1.0'
__license__ = 'public domain'


DB_FILE = 'eval-data.db'
DB_SCHEMA = '''
CREATE TABLE IF NOT EXISTS preferences (
        guild       TEXT PRIMARY KEY,
        prefix      TEXT NOT NULL,
        manage_role TEXT
);
CREATE TABLE IF NOT EXISTS commands (
        guild       TEXT NOT NULL,
        command     TEXT NOT NULL,
        source      TEXT NOT NULL,
        help        TEXT,
        PRIMARY KEY (guild, command)
);
'''


class EvalException(Exception):
    pass


class EvalClient(discord.Client):

    DEFAULT_PREFIX = '!'
    JS_TIMEOUT = 10
    JS_MEMORY = 50

    def __init__(self, database, *args, **kwargs):
        self._db = database
        super().__init__(*args, **kwargs)


    # events
    async def on_ready(self):
        logging.info('Connected to Discord')

    async def on_guild_join(self, guild):
        logging.info('Joining guild %s', guild.name)
        await self._init_guild(guild)
        await notify(guild.text_channels[0],
                     "Eval Bot in the house. Say '!help' for help.")

    async def on_guild_remove(self, guild):
        logging.info('Leaving guild %s', guild.name)
        guild_sf = str(guild.id)
        self._db.execute('DELETE FROM preferences WHERE guild=:guild', (guild_sf,))
        self._db.execute('DELETE FROM commands WHERE guild=:guild', (guild_sf,))
        self._db.commit()

    async def on_message(self, message):
        if message.author == self.user or not message.guild:
            return

        guild_sf = str(message.guild.id)
        cursor = self._db.execute(
                'SELECT prefix FROM preferences WHERE guild=?', (guild_sf,))
        result = cursor.fetchone()
        if result is None:
            await self._init_guild(message.guild)
            prefix = EvalClient.DEFAULT_PREFIX
        else:
            prefix = result[0]

        if message.content.startswith(prefix):
            split = message.content.split(maxsplit=1)
            command = split[0][len(prefix):].lower()
            if len(split) == 1:
                args_string = ''
            else:
                args_string = split[1]
            await self._do_command(message, command, args_string)


    async def _init_guild(self, guild):
        guild_sf = str(guild.id)
        self._db.execute(
                '''INSERT INTO preferences (guild, prefix, manage_role)
                   VALUES (?, ?, ?)''', (guild_sf, EvalClient.DEFAULT_PREFIX, None))
        self._db.commit()

    async def _do_command(self, message, command, args_string):
        try:
            if command == 'help':
                await self._help_command(message)
            elif command == 'evalprefix':
                self._authenticate(message)
                await self._prefix_command(message, args_string)
            elif command == 'role':
                self._authenticate(message)
                await self._role_command(message, args_string)
            elif command == 'set':
                self._authenticate(message)
                await self._set_command(message, args_string)
            elif command == 'sethelp':
                self._authenticate(message)
                await self._set_help_command(message, args_string)
            elif command == 'remove':
                self._authenticate(message)
                await self._remove_command(message, args_string)
            elif command == 'show':
                await self._show_command(message, args_string)
            else:
                await self._user_command(message, command, args_string)
        except EvalException as error:
            await notify(message.channel, error)

    def _authenticate(self, message):
        guild = message.guild
        guild_sf = str(guild.id)
        cursor = self._db.execute(
                'SELECT manage_role FROM preferences WHERE guild=?', (guild_sf,))
        role_sf = cursor.fetchone()[0]
        if role_sf is not None:
            role = next((role for role in guild.roles
                         if str(role.id) == role_sf), None)
            if role is not None and role not in message.author.roles:
                raise EvalException('You are not authorized to manage commands')


    # commands
    async def _help_command(self, message):
        builtins = {
            'help': 'Show this help',
            'evalprefix': "Change this bot's command prefix",
            'role': 'Set a required role to manage commands',
            'set': 'Add or update a custom command',
            'sethelp': 'Add help text for a custom command',
            'remove': 'Remove a custom command',
            'show': 'Retrieve the JavaScript source of a command'
            }
        def custom_commands(guild):
            table = {}
            guild_sf = str(guild.id)
            cursor = self._db.execute(
                    'SELECT command, help FROM commands WHERE guild=?', (guild_sf,))
            for row in cursor.fetchall():
                command, text = row
                if text is None or text == '':
                    text = '(no help text set)'
                table[command] = text
            return table
        guild = message.guild
        customs = custom_commands(guild)

        def print_table(prefix, command_length, text_map):
            result = ''
            for command, text in text_map.items():
                result += prefix
                result += command.ljust(command_length)
                result += ' : '
                result += text
                result += '\n'
            return result
        def max_length(text_map): return (max(len(key) for key in text_map.keys())
                                          if len(text_map) > 0 else 0)
        length = max(max_length(builtins), max_length(customs))
        def get_prefix(guild):
            guild_sf = str(guild.id)
            cursor = self._db.execute(
                    'SELECT prefix FROM preferences WHERE guild=?', (guild_sf,))
            result = cursor.fetchone()
            return result[0]
        prefix = get_prefix(guild)

        text = '```'
        text += '-- General --\n'
        text += print_table(prefix, length, builtins)
        text += '\n'
        text += '-- This Server --\n'
        if len(customs) == 0:
            text += '(no commands yet)'
        else:
            text += print_table(prefix, length, customs)
        text += '```'
        await message.channel.send(text)

    async def _prefix_command(self, message, args_string):
        if not args_string:
            raise EvalException('Expected usage: evalprefix <new prefix>')
        elif len(args_string) != 1:
            raise EvalException('New prefix must be a single character')

        guild_sf = str(message.guild.id)
        self._db.execute('UPDATE preferences SET prefix=? WHERE guild=?',
                         (args_string, guild_sf))
        self._db.commit()

    async def _role_command(self, message, args_string):
        if not args_string:
            raise EvalException('Expected usage: role <new role>')

        guild = message.guild
        role = next((role for role in guild.roles
                     if role.name == args_string), None)
        if role is None:
            raise EvalException("No such role '%s' exists" % args_string)

        guild_sf = str(guild.id)
        role_sf = str(role.id)
        self._db.execute('UPDATE preferences SET manage_role=? WHERE guild=?',
                         (role_sf, guild_sf))
        self._db.commit()
        await notify(message.channel, 'Okay')

    async def _set_command(self, message, args_string):
        split = args_string.split(maxsplit=1)
        if not split or len(split) == 1:
            raise EvalException('Expected usage: set <command> <javascript code>')

        function = split[0].lower()
        if self._is_builtin(function):
            raise EvalException('You cannot override a built-in command.')

        guild_sf = str(message.guild.id)
        source = split[1]
        cursor = self._db.execute(
                'SELECT EXISTS (SELECT 1 from commands WHERE guild=? AND command=?)',
                (guild_sf, function))
        if cursor.fetchone()[0] == 0:
            self._db.execute(
                    '''INSERT INTO commands (guild, command, source, help)
                       VALUES (?, ?, ?, ?)''', (guild_sf, function, source, None))
        else:
            self._db.execute(
                    'UPDATE commands SET source=? WHERE guild=? AND command=?',
                    (source, guild_sf, function))

        self._db.commit()
        await notify(message.channel, 'Okay')

    async def _set_help_command(self, message, args_string):
        split = args_string.split(maxsplit=1)
        if not split or len(split) == 1:
            raise EvalException('Expected usage: set <command> <help text>')

        function = split[0].lower()
        if self._is_builtin(function):
            raise EvalException('You cannot override a built-in command.')

        guild_sf = str(message.guild.id)
        text = split[1]
        cursor = self._db.execute(
                'SELECT EXISTS (SELECT 1 from commands WHERE guild=? AND command=?)',
                (guild_sf, function))
        if cursor.fetchone()[0] == 0:
            raise EvalException("No such command '%s' exists" % function)

        self._db.execute(
                'UPDATE commands SET help=? WHERE guild=? AND command=?',
                (text, guild_sf, function))
        self._db.commit()
        await notify(message.channel, 'Okay')

    async def _remove_command(self, message, args_string):
        if not args_string:
            raise EvalException('Expected usage: remove <command>')

        function = args_string.split()[0].lower()
        if self._is_builtin(function):
            raise EvalException('You cannot delete a built-in command.')

        guild_sf = str(message.guild.id)
        cursor = self._db.execute(
                'SELECT EXISTS (SELECT 1 from commands WHERE guild=? AND command=?)',
                (guild_sf, function))
        if cursor.fetchone()[0] == 0:
            raise EvalException("No such command '%s' exists" % function)

        self._db.execute('DELETE FROM commands WHERE guild=? AND command=?',
                         (guild_sf, function))
        self._db.commit()
        await notify(message.channel, 'Okay')

    async def _show_command(self, message, args_string):
        if not args_string:
            raise EvalException('Expected usage: show <command>')

        function = args_string.split()[0].lower()
        if self._is_builtin(function):
            raise EvalException('Built-in commands do not have JavaScript code.')

        guild_sf = str(message.guild.id)
        cursor = self._db.execute(
                'SELECT source FROM commands WHERE guild=? AND command=?',
                (guild_sf, function))
        result = cursor.fetchone()
        if result is None:
            raise EvalException("No such command '%s' exists" % function)

        source = result[0]
        await message.channel.send('```%s```' % source)

    async def _user_command(self, message, command, args_string):
        guild_sf = str(message.guild.id)
        cursor = self._db.execute(
                'SELECT source FROM commands WHERE guild=? AND command=?',
                (guild_sf, command))
        result = cursor.fetchone()
        if result is None:
            raise EvalException("Unknown command '%s'" % command)

        source = result[0]
        args = args_string.split()
        try:
            returned = execute_javascript(command, source, args)
        except py_mini_racer.MiniRacerBaseException as error:
            raise EvalException(str(error))
        else:
            if returned == '':
                await notify(message.channel, '(empty string)')
            else:
                await message.channel.send(str(returned))

    def _is_builtin(self, command):
        return command.lower() in ['help', 'evalprefix', 'role', 'set',
                                   'sethelp', 'remove', 'show']


def execute_javascript(function, source, args):
    interpreter = py_mini_racer.MiniRacer()
    interpreter.eval('%s = function () { %s }' % (function, source))

    def stringify(s): return '"%s"' % s.replace('"', '\\"')
    eval_args = ','.join(stringify(a) for a in args)
    return interpreter.eval('%s(%s)' % (function, eval_args),
                            timeout=EvalClient.JS_TIMEOUT, max_memory=JS_MEMORY)


async def notify(channel, message):
    await channel.send('**%s**' % message)


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Usage:', sys.argv[0], '<Discord token>', file=sys.stderr)
        sys.exit(1)

    logging.basicConfig(level=logging.INFO)
    token = sys.argv[1]

    with sqlite3.connect(DB_FILE) as database:
        database.executescript(DB_SCHEMA)
        logging.info('Initialized database')

        client = EvalClient(database)
        client.run(token)
