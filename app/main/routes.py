# sanity check route
from app.main import bp
from database import Session
from app.wa_messages import get_messages

session = Session()
@bp.route('/', methods=['GET'])
def index():
 return "Hello World"

@bp.route('/messages', methods=['GET'])
def messages():
 return get_messages(session)
