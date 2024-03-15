

from trytond.model import ModelSQL, ModelView, fields
from datetime import date, datetime

from sql.aggregate import Count
from trytond.pyson import Eval, Bool, If

from trytond.pool import Pool
from trytond.transaction import Transaction
from trytond.model import Unique

from trytond.model.exceptions import ValidationError

from trytond.exceptions import UserError

from sql import *
from sql.aggregate import *
from sql.conditionals import *

from trytond.report import Report


print("Checking Library models")

class Author(ModelSQL, ModelView):
    'Author'

    __name__ = 'library.author'
    name = fields.Char('Name', required=True)   
    dni = fields.Char('DNI', required=False)
    gender = fields.Selection([('man', 'Man'), ('woman','Woman')], 'Gender')
    birth_date = fields.Date('Author Birth Date',
                              required=True,
                              states={'required': Bool(Eval('dni', 'False'))},
                              depends=['birth_date']
                              )
    
    books = fields.One2Many('library.book', 'author', 'Books')  # One Author -> Many Books


    #CREATING A FUNCTION FIELD
    age = fields.Function(fields.Integer('Age',readonly=True, states={'invisible':False }), 'getter_ages')

    number_of_books = fields.Function(fields.Integer('Number of Books', readonly=True, help="No Edit FIeld"), 'gettter_number_of_books')   
    # my_search_field = fields.Function(fields.Many2Many('library.book-library.genre', None, None,  'Genre'),'getter_genres', searcher='searcher_my_field' )

    party = fields.Many2One('party.party', 'Party', required=False,
            ondelete='CASCADE', domain=[(('biological_sex', '!=', ' '))])

    #on Change
    @fields.depends('birth_date')
    def on_change_age(self, name=None):
        current_time = date.today()
        print(f"on_change_with_age TEst.... API....")
        author_age = current_time.year - self.birth_date.year
        print(f'{self.birth_date.year} < {current_time.year} and {self.birth_date.month} <= {current_time.month}')
        if (self.birth_date.year < current_time.year and self.birth_date.month <= current_time.month):
             if (current_time.day> self.birth_date.day):
                return author_age
             return author_age
        
        author_age= author_age - 1
        return author_age
    
    
    @fields.depends('books')
    def on_change_books(self):
         print("Calling Books Objects...")
         if not self.books:
              self.number_of_books = 0
              return
         
                

    @classmethod
    def getter_ages(cls,authors,name):
        current_time = date.today()
        reset_all_ages = {author.id:0 for author in authors}
        authors_inf = Table('library_author')

        quer = authors_inf.select(authors_inf.id,authors_inf.birth_date)
        cursor = Transaction().connection.cursor()
        cursor.execute(*quer)
        data = cursor.fetchall()


        
        def ageCalculation(date):
            author_age = current_time.year - date.year
            if (date.year < current_time.year and date.month <= current_time.month):
              if (current_time.day> date.day):
                return author_age
            return author_age-1
        
            
        for  author,dates in  data:
          reset_all_ages[author] = ageCalculation(dates)

        return reset_all_ages
    
   
    @classmethod
    def gettter_number_of_books(cls, authors, name):
        print('Printing Authors....')
        

        Book = Pool().get('library.book')
        book = Book.__table__()

        # from sql import Table
        # book = Table('library_book')

        new_result = {x.id:0 for x in authors} # {1: 0, 2: 0, 3: 0, 4: 0}
        authors_id_list = [author.id for author in authors]
        
        
         
        methods = [actionMethods for actionMethods in  dir(Transaction().connection) if actionMethods.startswith("__") is False]
        print(methods)
        
        cursor = Transaction().connection.cursor()
        cursor.execute(*book.select(book.author,  Count(book.id), where=book.author.in_(authors_id_list), group_by=[book.author] ))

        # print(*book.select(book.author,  Count(book.id), where=book.author.in_([1,2,3,4]), group_by=[book.author]  ))
        # cursor.execute(*book.select(book.author,  Count(book.id), where=book.author.in_([1,2,3,4]), group_by=[book.author]  ))
        cursor.execute(*book.select(book.author,  Count(book.id), where=book.author.in_(authors_id_list), group_by=[book.author] ))
        some_test = cursor.fetchall()

        for author_id, counter in some_test:
            new_result[author_id] = counter
        
        #print("Countet")
        #print(new_result)
        return new_result
    
    @classmethod
    def getter_genres(cls, authors, name):

        print('Takeing Teh Action Gennres ')
        DIC_AUTHORS= {author.id:author.id for author in authors}
        print(DIC_AUTHORS)

        return DIC_AUTHORS
        return LIST_AUTJORS_GENRES
    
    
    @classmethod
    def searcher_my_field(self, name, clauser):
        print("Searcher is invoked")
        return []


              



class BookEditor(ModelSQL, ModelView):
    'Editor'
    __name__ = 'library.editor'
    _rec_name = 'editor_name'

    editor_name = fields.Char('Editor Name', required=True)
    genres = fields.Many2Many('library.editor-library.genre', 'genre','editor', 'Genres')
    creation_date = fields.Date('Date Editor Creation', required=True)



class Genre(ModelSQL, ModelView):
    'Genre'
    __name__ = 'library.genre'
    genre_type = fields.Char('Genre', required=True, help="Type the Book Gennre")   
    


class Book(ModelSQL, ModelView):
     'Book'
     __name__ = 'library.book'
     _rec_name = 'book_title'
     
       # Many2One Field #
 
     author = fields.Many2One('library.author', 'Authors', ondelete='RESTRICT', domain=[('birth_date', '<', Eval('publiced_date', False))], depends=['publiced_date'], required=False)  #Many Books One Author

     editor = fields.Many2One('library.editor', 'Editor', ondelete='RESTRICT',   domain=[('creation_date', '<=', Eval('publiced_date', False))], depends=['publiced_date'], required=True)

     genre= fields.Many2Many('library.book-library.genre', 'book_title','genre', 'Genres')
    
    #  last_book_comment = fields.Function(fields.Integer('library.book.bookcomment','comment','Last Comment'), 'getter_last_comment_book_counter')

     latest_exemplary = fields.One2Many('library.book.bookcomment','book','Latest exemplary')




     @classmethod
     @ModelView.button_action('library.act_comment')
     def create_exemplaries(cls, books):
         print("Invokibg Create Exmplary....")
         pass
        


     @fields.depends('latest_exemplary',)
     def on_change_latest_exemplary(self, books, name):
       print("Making Call")
       # YOU NEED TO CREATE A QUIERY 
    #    BookComment = Pool().get('library.book.bookcomment')
    #    bookComment = BookComment.__table__()
    #    index_books = {book.id:0 for book in books}


    #    array_of_books_id = [book.id for book in books]     
    #    cursor = Transaction().connection.cursor()
    #    cursor.execute(*bookComment.select(bookComment.book, Count(bookComment.id), where=bookComment.book.in_(array_of_books_id), group_by=[bookComment.book]))
    #    some_test = cursor.fetchall()
       
    #    print(some_test)
       
    #    for book_id, counter in some_test:
    #        print(index_books[book_id])
                
    #    return index_books
    #    latest = None
    #    for exemplary in self.exemplaries:
    #      if not exemplary.acquisition_date:
    #          continue
    #      if not latest or(latest.acquisition_date < exemplary.acquisition_date):
    #         latest = exemplary


     # UNIQUE FIELDS #
     book_title = fields.Char('Book Title', required=True) 
     page_count = fields.Integer('Page Count', help='The total of page on the book.')
     description = fields.Text('Description', help=f'Generate Book description')
     publiced_date = fields.Date('Publich Date')
     bin_code = fields.Integer('Book Code', help=f'Book code accesss.')
       


     edition_stopped = fields.Boolean('Edition stopped', help=f'If True, this book will not be printed again in this version in {date.today().year}')
     
     # Auto Field
     @fields.depends('editor', 'genre')
     def on_change_editor(self):
         print(self.genre)
         print(self.editor.genres[0])
         if not self.editor:
            return 
         if self.genre and (self.genre not in self.editor.genres):
            print("Empty genre")
            self.genre = None
         if not self.genre and len(self.editor.genres) == 1:
            self.genre = {1}

     # Auto Field
     @fields.depends('description')
     def on_chnage_with_description(self):
         if self.description: 
             return self.description
        


     @classmethod
     def __setup__(cls):
        super(Book, cls).__setup__()

        print("__INCOING SET UP____")
        t = cls.__table__()
        cls._sql_constraints +=[('bin_code', Unique(t, t.bin_code), 
                                 'The value Must to be Unique')] 
        cls._buttons.update({
         'create_exemplaries':{}
        })



        
        
     @fields.depends('author')
     def on_change_author(self):
         print("Calling Books's author form model books Objects...")
        #  self.book_title ='ALL IN UPPER CASE'
         return
    
     @classmethod
     def validate(cls, books):
        print("Validation is invoked by tryton")
        for eachBook in books:
            print(len(f'{eachBook.bin_code}'))
            if (len(f'{eachBook.bin_code}') > 3):
                print("Error")
                raise UserError("this's a test too log")         
   

     @classmethod  
     def getter_last_comment_book_counter (clss, books, name): 
          # Create POOl #
        BookComment = Pool().get('library.book.bookcomment')
        bookComment = BookComment.__table__()
        print(books)
          
          
        object_setter= {x.id:5 for x in books }
        array = [book.id for book in books]

        # cursor = Transaction().connection.cursor()
        # cursor.execute(*bookComment.select(bookComment.book, Count(bookComment.id), where=bookComment.book.in_(array), group_by=[bookComment.book]))
        # books_comments= cursor.fetchall()

        # print(books_comments)
        # for book_id, bookCommentsCount in books_comments:
        #      print(f'Book id {book_id} book count {bookCommentsCount}')
        #     #  object_setter[book_id]=bookCommentsCount 

        return object_setter

         
     






class BookComment(ModelSQL,ModelView):
     'Comment'
     __name__ = 'library.book.bookcomment'
     book = fields.Many2One('library.book', 'Book', ondelete='CASCADE', required=False)
     acquisition_price = fields.Numeric('Acquisition Price', digits=(16,2), domain=["OR",('acquisition_price','=',None), ('acquisition_price','>=', 0)]) 
     acquisition_date = fields.Date('Acquisition Date')
     addInformation = fields.Text('Inf',required=False)
     indentifier = fields.Char(
         'Identification',
     )


     @classmethod
     def default_acquisition_date(cls):
         pool = Pool()
         Date = pool.get('ir.date')
         return Date.today()


     @classmethod
     def __setup__(cls):
        super(BookComment, cls).__setup__()
        t = cls.__table__()
        cls._sql_constraints +=[
            ('indentifier', Unique(t, t.indentifier), 'The value Must to be Unique.')
        ] 


     
    

    #  def get_rec_name(self, nane):
    #      print("Gettting Records Name...")
    #      print(nane)
    #      return  '{}'.format(self.book.rec_name)
     



class BooksGenre(ModelSQL):
      'Book Relation..'
      __name__='library.book-library.genre'
      genre = fields.Many2One('library.genre','Genre', required=True, ondelete='RESTRICT')
      book_title = fields.Many2One('library.book', 'Book', required=True, ondelete='RESTRICT')

             


class BookComentRelation(ModelSQL):
    'Relation BooK and Comment'
    pass
    __name__ = 'library.book.bookcomment-library.editor'
    comment = fields.Many2One('library.book.bookcomment', 'Comment', required=False, ondelete='RESTRICT')        
          


class EditorGenreRelation(ModelSQL):
    'Editor - Genre relation'
    __name__ = 'library.editor-library.genre'

    editor = fields.Many2One('library.editor', 'Editor', required=True,
        ondelete='CASCADE')
    
    genre = fields.Many2One('library.genre', 'Genre', required=True,
        ondelete='RESTRICT')

