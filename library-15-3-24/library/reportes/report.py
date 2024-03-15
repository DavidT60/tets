
from trytond.model import ModelSQL, ModelView, fields
from datetime import date, datetime

from sql.aggregate import Count
from trytond.pyson import Eval, Bool, If

from trytond.pool import Pool
from trytond.transaction import Transaction
from trytond.model import Unique

from trytond.model.exceptions import ValidationError

from trytond.exceptions import UserError
from trytond.report import Report


class authorReport(Report):
    __name__='library.book.report'
    
    @classmethod
    def get_context(cls, records, header, data):
        report_context = super().get_context(records, header, data)

        
        return report_context


class AuthorReport(Report):
    __name__='library.report'
    
    @classmethod
    def get_context(cls, records, header, data):
        report_context = super().get_context(records, header, data) # Call the original model from ReportS

        pool = Pool()
        Date = pool.get('ir.date')
        date = Date.today()
        
        print(header)

        Book = Pool().get('library.book')

        current_user = Pool().get('res.user')
        list_data =[record.name for record in current_user.search([]) if record.id==Transaction().user]
        print(list_data)

        records_inf = [record for record in Book.search([]) if record.author.id == data['id']]  
        books_meta = []

        for record in records_inf:
           books_meta.append({'title':record.book_title, 'publiced':record.publiced_date, 'editor': record.editor.editor_name, 'genre':[{'name_genre':genre_types.genre_type} for genre_types in record.genre]})


        print(books_meta)
        report_context['date'] = date
        report_context['company'] = "TEST"
        report_context['current_user']= list_data[0]
        report_context['books_inf'] = books_meta

        return report_context
    