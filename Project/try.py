from flask import safe_join

print safe_join('a', 'b').replace('\\', 'c')