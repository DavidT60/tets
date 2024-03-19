from trytond.pyson import Eval, Date
from trytond.exceptions import UserError

from datetime import date
# Wixard imports |-------------------------------------------------------
from trytond.model import ModelView, fields
from trytond.wizard import Wizard, StateView, StateTransition, StateAction
from trytond.wizard import Button
from trytond.transaction import Transaction
from trytond.pool import Pool


__all__ = [
   'CreateExemplaries',   
   'CreateExemplariesParametres',
   'CreateBooks',
   'CreateViewBook',
   'fullingCreateExemplariesParametres'
]


# this control all the actions...
class CreateExemplaries(Wizard):
    'Create Examplarie'
    __name__ = 'library.book.create_exemplaries'

    start_state = 'parameters'
    parameters = StateView('library.book.create_exemplaries.parametres',
    'library.create_exemplaries_parametres_view_form', [
        Button('Cancel', 'end', 'tryton-cancel'),
        Button('Create', 'create_exemplaries', 'tryton-go-next',
            default=True)])
    
    create_exemplaries = StateTransition()
    open_exemplaries = StateAction('library.act_comment')



    select_main = StateView('library.book.create_exemplaries.parametres.fuse',
    'library.fuse_select_main_view_form', [
        Button('Cancel', 'end', 'tryton-cancel'),
        Button('Preview', 'check_compatibility', 'tryton-go-next',
            default=True)])
    
    check_compatibility = StateTransition()
    open_exemplaries_cooment= StateAction('library.act_comment')


   #------------------------States Methods-------------------------------#


    def default_parameters(self, name):
         print("Opeing the action module...")
         if Transaction().context.get('active_model','')!= 'library.book':
             raise UserError("This is not the Book Module")
         
         return{
             'acquisition_date': date.today(),
             'book': Transaction().context.get('active_id'),
             'acquisition_price':0
         }
    

    def default_select_main(self, name):
        if self.select_main._default_values:
           return self.select_main._default_values
        Book = Pool().get('library.book')
        books = Book.browse(Transaction().context.get('active_ids'))
        return {'book': [x.id for x in books],
                'acquisition_date': date.today()
                }

    

    # overwirtten this class #
    def transition_create_exemplaries(self):
        if(self.parameters.acquisition_date and self.parameters.acquisition_date > date.today()):
            raise UserError(f'The Date must to be less ot equal to {date.day()}')
        
        # Inserting all the data in exemplary #
        Exemplary = Pool().get('library.book.bookcomment')
        to_insert = []
          
        exemplary = Exemplary()
        exemplary.book = self.parameters.book
        exemplary.acquisition_price = self.parameters.acquisition_price
        exemplary.acquisition_date = self.parameters.acquisition_date
        exemplary.addInformation = self.parameters.addInformation
        exemplary.indentifier = self.parameters.indentifier
        to_insert.append(exemplary)
        Exemplary.save(to_insert)

        return 'open_exemplaries'





    def transition_check_compatibility(self):
        print("Invoking Transaction Check Compability....")    
        return 'open_exemplaries_cooment'
    




    

class CreateBooks(Wizard):
     'Create a Book'
     __name__= 'library.author.create_book'
     start_state = 'parameters'

     #start: showing the documentation to the user how create a new Book
     parameters = StateView('library.author.create_book.parameters', 
                             'library.create_books_parametres_view_form',
                             [
                               Button('Cancel', 'end', 'tryton-cancel'),
                               Button('Create', 'create_book', 'tryton-go-next', default=True),
                               Button('Multiple', 'create_booker', 'tryton-go-next-Multiple'),

                             ],                           
                            )
     
     create_book = StateTransition() # Stay Static in the action before..
     create_booker = StateTransition() # Stay Static in the action before..


     open_books = StateAction('library.act_book')  # final State
     open_author = StateAction('library.act_author')  # final State




     def default_parameters(self, name):
         print("Opeing Action Module....")
         if Transaction().context.get('active_model','')!= 'library.author':
             raise UserError("This is not the Book Module")            

         return{
              'author':Transaction().context.get('active_id'),
              'publiced_date':date.today()
            }
     

     def transition_create_booker(self):
         print("Creating Transaction...")
         if(self.parameters.publiced_date > date.today()):
              raise UserError(f"You canot Publish at a date more tha the {date.today}")

         return 'open_author'

     
     def transition_create_book(self):
         print("Creating Transaction...")
         if(self.parameters.publiced_date > date.today()):
              raise UserError(f"You canot Publish at a date more tha the {date.today}")
            
         Book = Pool().get('library.book')
         to_insert = []
          
         book = Book()
         book.author = self.parameters.author
         book.editor = self.parameters.editor
         book.genre = self.parameters.genre
         book.book_title = self.parameters.book_title
         book.page_count = self.parameters.page_count
         book.description =self.parameters.description
         book.publiced_date =self.parameters.publiced_date
         book.bin_code =self.parameters.bin_code
         book.edition_stopped =self.parameters.edition_stopped
         to_insert.append(book)
         Book.save(to_insert)
         return 'open_books'

     



#----------------------------------------view-----------------------------------#


class CreateExemplariesParametres(ModelView):
    'Create Exemplarie Parametre'
    # Must to be like [way 1]
    #way 1__name__ = 'library.book.create_exemplaries_parametres'
    __name__ = 'library.book.create_exemplaries.parametres'
    
    book = fields.Many2One('library.book', 'Book', ondelete='CASCADE', required=False)
    acquisition_price = fields.Numeric( 'Acquisition Price', digits=(16,2),
                                        domain=["OR",('acquisition_price','=',None), 
                                       ('acquisition_price','>=', 0)]) 
    acquisition_date = fields.Date('Acquisition Date')
    addInformation = fields.Text('Inf',required=False)
    indentifier = fields.Char(
         'Identification',
     )




class fullingCreateExemplariesParametres(ModelView):
    'Create Exemplarie Parametre'
    # Must to be like [way 1]
    #way 1__name__ = 'library.book.create_exemplaries_parametres'
    __name__ = 'library.book.create_exemplaries.parametres.fuse'
    book = fields.Many2One('library.book', 'Book', ondelete='CASCADE', required=False)
    acquisition_date = fields.Date('Acquisition Date')







class CreateViewBook(ModelView):
      'Create Book View'

      
      __name__= 'library.author.create_book.parameters'

      #Passing Related FIelds# 
      author = fields.Many2One('library.author', 'Authors', ondelete='RESTRICT', domain=[('birth_date', '<', Eval('publiced_date', False))], depends=['publiced_date'], required=False)  #Many Books One Author
      editor = fields.Many2One('library.editor', 'Editor', ondelete='RESTRICT',   domain=[('creation_date', '<=', Eval('publiced_date', False))], depends=['publiced_date'], required=True)
      genre= fields.Many2Many('library.book-library.genre', 'book_title','genre', 'Genres')



      # UNIQUE FIELDS #
      book_title = fields.Char('Book Title', required=True) 
      page_count = fields.Integer('Page Count', help='The total of page on the book.')
      description = fields.Text('Description', help=f'Generate Book description')
      publiced_date = fields.Date('Publich Date')
      bin_code = fields.Integer('Book Code', help=f'Book code accesss.')
      edition_stopped = fields.Boolean('Edition stopped', help=f'If True, this book will not be printed again in this version in {date.today().year}')



