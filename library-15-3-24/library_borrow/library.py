from trytond.model import ModelSQL, ModelView, fields
from datetime import date, datetime

from sql.aggregate import Count
from trytond.pyson import Eval, Bool, If

from trytond.pool import Pool
from trytond.transaction import Transaction
from trytond.model import Unique

from trytond.model.exceptions import ValidationError

from trytond.exceptions import UserError
from trytond.pool import PoolMeta



class BookComment(metaclass=PoolMeta):
      __name__ = 'library.book.bookcomment'
      checkout = fields.One2Many('library.user.checkout', 'user', 'Checkouts', required=True)
      



class User(ModelSQL, ModelView):
     'Users'
     __name__= 'library.user'
     checkout = fields.One2Many('library.user.checkout', 'user', 'Checkouts', required=True)

class Checkout(ModelSQL,ModelView):
      'Checkout'
      __name__ = 'library.user.checkout'    
      user= fields.Many2One('library.user', 'User', required=True)
      exemplary = fields.Many2One('library.book.bookcomment', 'Exemplary', required=True)