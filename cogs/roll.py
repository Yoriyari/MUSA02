#===============================================================================
# Roll v1.3.2
# by Yoriyari
#===============================================================================
# Update History
# ..............................................................................
# 05 May 2024 - v1.3.2; Reworked help message import. Added error handling. -YY
# 04 Nov 2023 - v1.3.1; Added math aliases for invoking the roll command. -YY
# 17 Apr 2022 - v1.3; Centralized help messages to one importable file. Added a
#               help command to this file. -YY
# 24 Jan 2022 - v1.2; Limited amount of dice and faces to prevent overloading
#               the bot and Discord's message size limit. Removed the repeated
#               callbacks to Expr in parsing. -YY
# 19 Jan 2022 - v1.1; Expanded file to use classes for expressions. Bot now
#               gives feedback on which dice rolled what and has been limit on
#               output length. Support added for multiplication, division,
#               parentheses, and (dis)advantage. -YY
# 06 Jan 2022 - v1.0; Started and finished file. Supports dice, plus, and minus.
#               -YY
#===============================================================================
# Notes
# ..............................................................................
# - Prevent a recursive function call stack overflow. Might be solved by writing
#   expression components to an array of sorts instead of doing this recursive
#   object thing. This should give a much larger upper limit. -YY
# - Improve math formula parsing. -YY
# - Extend to allow float computation. -YY
# - Add x and × as aliases to *. Consider similar for other symbols. -YY
# - It may be wise to have !math compute things with floats while !roll sticks
#   to integers. -YY
#===============================================================================
# Description
# ..............................................................................
# roll.py allows for dice rolls through Discord with the use of a dice formula.
# The dice themselves have the format XdY where X is the number of dice and Y is
# the number of faces of the dice.
# Additionally, different types of dice and literal values can be used in more
# complex mathematical expressions with the use of operators such as addition,
# subtraction, multiplication, and division.
# Also, advantage or disadvantage can be appended to the end of the formula to
# roll the expression twice and take the best or worst result, respectively.
#===============================================================================

#Import Modules
import discord
from discord.ext import commands

from common.error_message import send_error
from common.help_message import send_help

import random

#Binary Operator class
class BinOp:
    def __init__(self, op: str, left: str, right: str):
        self.op = op
        self.left = parse(left)
        self.right = parse(right)

    def sum(self):
        if self.op == "+":
            return self.left.sum() + self.right.sum()
        if self.op == "-":
            return self.left.sum() - self.right.sum()
        if self.op == "*":
            return self.left.sum() * self.right.sum()
        if self.op == "/":
            return self.left.sum() // self.right.sum()

    def to_string(self):
        return f"{self.left.to_string()} {self.op} {self.right.to_string()}"

#Parentheses class
class Parentheses:
    def __init__(self, inner: str):
        self.inner = parse(inner)

    def sum(self):
        return self.inner.sum()

    def to_string(self):
        return f"({self.inner.to_string()})"

#Die class
class Dice:
    def __init__(self, count: int, faces: int):
        self.count = count
        self.faces = faces
        self.rolls = self.roll()

    def roll(self):
        if self.count > 1000 or len(str(self.faces)) > 1500:
            return None
        rolls = []
        for _ in range(self.count):
            rolls.append(random.randint(1, self.faces))
        return rolls

    def sum(self):
        return sum(self.rolls)

    def to_string(self):
        msg = f"{self.count}d{self.faces} ❰"
        for i in range(len(self.rolls)):
            if i > 0:
                msg += ", "
            if len(msg) + len(f"{self.rolls[i]}") > 100:
                msg += "..."
                break
            elif self.rolls[i] == 1 or self.rolls[i] == self.faces:
                msg += f"**{self.rolls[i]}**"
            else:
                msg += f"{self.rolls[i]}"
        msg += "❱"
        return msg

#Literal class
class Lit:
    def __init__(self, value: int):
        self.value = value

    def sum(self):
        return self.value

    def to_string(self):
        return f"{self.value}"

#Expression class
class Expr:
    def __init__(self, expr: str):
        self.expr = expr
        self.component = parse(expr)

    def sum(self):
        try:
            return self.component.sum()
        except:
            return None

    def to_string(self):
        try:
            return self.component.to_string()
        except:
            return None

def parse(expr):
    #Parentheses
    active_parentheses = index_parentheses(expr)
    if any([len(p) != 2 for p in active_parentheses]):
        return None
    if len(active_parentheses) > 0 and active_parentheses[0][0] == 0 and active_parentheses[0][1] == len(expr)-1:
        try:
            return Parentheses(expr[1:-1])
        except:
            return None
    #Binary Operators
    i_add, i_min, i_mul, i_div = index_operators(expr, active_parentheses)
    #BinOp Addition
    if i_add >= 0 and (i_min < 0 or i_add > i_min):
        try:
            return BinOp("+", expr[:i_add], expr[i_add+1:])
        except:
            return None
    #BinOp Subtraction
    elif i_min >= 0:
        try:
            return BinOp("-", expr[:i_min], expr[i_min+1:])
        except:
            return None
    #BinOp Multiplication
    i_mul, i_div = expr.find("*"), expr.find("/")
    if i_mul >= 0 and (i_div < 0 or i_mul > i_div):
        try:
            return BinOp("*", expr[:i_mul], expr[i_mul+1:])
        except:
            return None
    #BinOp Division
    elif i_div >= 0:
        try:
            return BinOp("/", expr[:i_div], expr[i_div+1:])
        except:
            return None
    #Dice
    if "d" in expr:
        try:
            comp = expr.split("d", 1)
            if comp[0] == "":
                comp[0] = "1"
            comp = [int(n) for n in comp]
            return Dice(comp[0], comp[1])
        except:
            return None
    #Literals
    try:
        return Lit(int(expr))
    except:
        return None

def index_parentheses(expr):
    active_parentheses = []
    for i in range(len(expr)):
        if expr[i] == "(":
            active_parentheses.append([i])
        if expr[i] == ")":
            for p in reversed(active_parentheses):
                if len(p) < 2:
                    p.append(i)
                    break
    return active_parentheses

def index_operators(expr, active_parentheses):
    i_add, i_min, i_mul, i_div = -1, -1, -1, -1
    for i in range(len(expr)):
        if any([i >= p[0] and i <= p[1] for p in active_parentheses]):
            continue
        if i_add == -1 and expr[i] == "+":
            i_add = i
        if i_min == -1 and expr[i] == "-":
            i_min = i
        if i_mul == -1 and expr[i] == "*":
            i_mul = i
        if i_div == -1 and expr[i] == "/":
            i_div = i
    return i_add, i_min, i_mul, i_div

#Cog Setup
class Roll(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        print("Roll cog loaded.")

    #Roll dice
    @commands.command(aliases=["r", "math", "calculate", "calculator", "calc", "compute", "solve"])
    async def roll(self, ctx, *formula):
        try:
            if formula == [] or formula == ["help"]:
                await send_help(ctx.channel.send, "roll")
                return
            advantage = detect_advantage(formula)
            formula = remove_formula_spaces(formula, advantage)
            if count_recursions(formula) > 300:
                await ctx.channel.send("Too many components to dice formula.")
                return
            result = []
            for _ in range(1+abs(advantage)):
                result.append(Expr(formula))
            msg = f"{ctx.author.mention}\n**Result:** "
            if not any(r.sum() == None for r in result):
                kept_result1 = (advantage == -1 and result[0].sum() > result[1].sum()) or (advantage == 1 and result[0].sum() < result[1].sum())
                if advantage != 0:
                    if kept_result1:
                        msg += f"~~{result[0].to_string()}~~ **VS** {result[1].to_string()}"
                    else:
                        msg += f"{result[0].to_string()} **VS** ~~{result[1].to_string()}~~"
                else:
                    msg += f"{result[0].to_string()}"
                if len(msg) > 400:
                    msg = f"{msg[:400]}"
                    if msg.count("**") % 2 == 1:
                        msg += "**"
                    if msg.count("~~") % 2 == 1:
                        msg += "~~"
                    msg += " ..."
                msg += f"\n**Total:** "
                if kept_result1:
                    msg += f"{result[1].sum()}"
                else:
                    msg += f"{result[0].sum()}"
            else:
                msg = "Invalid dice formula."
            if len(msg) > 2000:
                msg = "Dice formula is too long."
            await ctx.channel.send(msg)
        except Exception as e:
            await send_error(self.client, e, reference=ctx.message.jump_url)

def detect_advantage(formula):
    if len(formula) > 1:
        if formula[-1].lower().startswith("adv"):
            return 1
        if formula[-1].lower().startswith("dis"):
            return -1
    return 0

def remove_formula_spaces(formula, advantage):
    if advantage != 0:
        formula = formula[:-1]
    formula = "".join(formula).lower()
    return formula

def count_recursions(f):
    return f.count("+") + f.count("-") + f.count("*") + f.count("/") + f.count("(")

async def setup(client):
    await client.add_cog(Roll(client))
