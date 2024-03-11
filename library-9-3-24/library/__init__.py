
from trytond.pool import Pool

from . import library
from . import wizard
from . import party


print("Testing library module")

"""
    register:
      it will be called by the server during the server start up to register the module. 

      it will create the tables based in the register and the class's __name__ on it
      .... library_authoer

      it will look in the magic library.Author __name__
"""
def register():
     print('server calling register pool.....')
     Pool.register(
          library.Author,
          library.Genre,
          library.Book,
          library.BookEditor,
          library.EditorGenreRelation, 
          library.BookComment,
          library.BookComentRelation,
          library.BooksGenre,
          wizard.CreateExemplariesParametres,
          wizard.CreateViewBook,
          wizard.fullingCreateExemplariesParametres,
          party.Party,
          module='library',
          type_='model'
      )
     Pool.register(
          wizard.CreateExemplaries,
          wizard.CreateBooks,
          module='library',
          type_='wizard',
     )