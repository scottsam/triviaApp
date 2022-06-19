import os
import random
from email.mime import nonmultipart

from flask import Flask, abort, jsonify, request
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from models import Category, Question, setup_db

QUESTIONS_PER_PAGE = 10


def paginated_questions(request, selection):
    page = request.args.get("page", 1, type=int)  # get a shelf and populate with books
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE
    questions = [question.format() for question in selection]
    cur_questions = questions[start:end]
    return cur_questions


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)

    """
    @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
    """
    cors = CORS(app, resources={r"/api/*": {"origins": "*"}})

    """
    @TODO: Use the after_request decorator to set Access-Control-Allow
    """
    # getting the access control headers
    @app.after_request
    def after_request(response):
        response.headers.add(
            "Access-Control-Allow-Headers", "Content-Type,Authorization,true"
        )
        response.headers.add(
            "Access-Control-Allow-Methods", "GET,PATCH,POST,DELETE,OPTIONS"
        )
        return response

    """
    @TODO:
    Create an endpoint to handle GET requests
    for all available categories.
    """

    @app.route("/categories")
    def get_categories():
        # get all categories
        categories = Category.query.all()

        # create an empty category dict object
        cat_obj = {}

        # adding all categories to the dict(`id: category_string`)
        for category in categories:
            cat_obj[category.id] = category.type

        return jsonify({"success": True, "categories": cat_obj})

    """
    @TODO:
    Create an endpoint to handle GET requests for questions,
    including pagination (every 10 questions).
    This endpoint should return a list of questions,
    number of total questions, current category, categories.

    TEST: At this point, when you start the application
    you should see questions and categories generated,
    ten questions per page and pagination at the bottom of the screen for three pages.
    Clicking on the page numbers should update the questions.
    """

    @app.route("/questions")
    def get_questions():
        try:
            # querying all questions
            selections = Question.query.order_by(Question.id).all()
            

            # get the total num of questions
            totalQuestions = len(selections)

            # get current questions in a page (10q)
            currentQuestions = paginated_questions(request, selections)

            # if the page number is not found
            if len(currentQuestions) == 0:
                abort(404)

            # get all categories
            categories = Category.query.all()
        
        
            categoriesDict = {}
            for category in categories:
                categoriesDict[category.id] = category.type

            return jsonify(
                {
                    "success": True,
                    "questions": currentQuestions,
                    "totalQuestions": totalQuestions,
                    "categories": categoriesDict,
                    "currentCategory": categories[3].format()["type"]
                }
            )
        except:
            abort(404)

    """
    @TODO:
    Create an endpoint to DELETE question using a question ID.

    TEST: When you click the trash icon next to a question, the question will be removed.
    This removal will persist in the database and when you refresh the page.
    """

    @app.route("/questions/<int:question_id>", methods=["DELETE"])
    def delete_question(question_id):
        try:
            # query Question table to get the question with the question_id params
            question = Question.query.filter(Question.id == question_id).one_or_none()
            if question is None:
                abort(404)
            question.delete()
            selections = Question.query.order_by(Question.id).all()
            current_questions = paginated_questions(request, selections)

            return jsonify(
                {
                    "success": True,
                    "deleted": question_id,
                    "totalQuestions": len(Question.query.all()),
                }
            )
        except:
            abort(422)

    """
    @TODO:
    Create an endpoint to POST a new question,
    which will require the question and answer text,
    category, and difficulty score.

    TEST: When you submit a question on the "Add" tab,
    the form will clear and the question will appear at the end of the last page
    of the questions list in the "List" tab.
    """

    @app.route("/questions", methods=["POST"])
    def add_question():
        # creating an empty dict to  get data from frontend
        body = request.get_json()

        # getting data from the frontend
        question = body.get("question", None)
        answer = body.get("answer", None)
        category = body.get("category", None)
        difficulty = body.get("difficulty", None)

        try:
            # add to Database
            question = Question(
                question=question,
                answer=answer,
                category=category,
                difficulty=difficulty,
            )
            question.insert()

            # send back the current questions, to update front end
            selection = Question.query.order_by(Question.id).all()
            current_questions = paginated_questions(request, selection)

            return jsonify(
                {
                    "success": True,
                }
            )

        except:
            abort(405)

    """
    @TODO:
    Create a POST endpoint to get questions based on a search term.
    It should return any questions for whom the search term
    is a substring of the question.

    TEST: Search by any phrase. The questions list will update to include
    only question that include that string within their question.
    Try using the word "title" to start.
    """

    @app.route("/questions/search", methods=["POST"])
    def search():
        body = request.get_json()
        search_term = body.get(
            "searchTerm", None
        )  # getting the string from the search input
        try:

            if search_term is None or len(search_term)==0:

                abort(404)

            questions = Question.query.filter(
                Question.question.ilike("%{}%".format(search_term))
            ).all()
            current_questions = paginated_questions(request, questions)

            return jsonify(
                {
                    "success": True,
                    "questions": current_questions,
                    "totalQuestions": len(questions),
                    "currentCategory": None,
                }
            )
        except:
            abort(404)

    """
    @TODO:
    Create a GET endpoint to get questions based on category.

    TEST: In the "List" tab / main screen, clicking on one of the
    categories in the left column will cause only questions of that
    category to be shown.
    """

    @app.route("/categories/<int:category_id>/questions")
    def category_questions(category_id):
        try:
            # filter category with the given category_id
            category = Category.query.filter_by(id=category_id).one_or_none()
            if category is None:
                abort(404)

            # filter questions using the category property
            questions = Question.query.filter_by(category=str(category_id)).all()
            current_questions = paginated_questions(request, questions)
            return jsonify(
                {
                    "success": True,
                    "questions": current_questions,
                    "totalQuestions": len(questions),
                    "currentCategory": category.type,
                }
            )

        except:
            abort(422)

    """
    @TODO:
    Create a POST endpoint to get questions to play the quiz.
    This endpoint should take category and previous question parameters
    and return a random questions within the given category,
    if provided, and that is not one of the previous questions.

    TEST: In the "Play" tab, after a user selects "All" or a category,
    one question at a time is displayed, the user is allowed to answer
    and shown whether they were correct or not.
    """

    @app.route("/quizzes", methods=["POST"])
    def quiz():
        # get the qestion category an the previous question
        body = request.get_json()
        quizCategory = body.get("quiz_category")
        previousQuestion = body.get("previous_questions")

        try:
            if quizCategory["id"] == 0:
                questionsQuery = Question.query.all()
            else:
                questionsQuery = Question.query.filter_by(
                    category=quizCategory["id"]
                ).all()

            randomIndex = random.randint(0, len(questionsQuery) - 1)
            while len(questionsQuery) > 0:
                nextQuestion = questionsQuery[randomIndex]
                if nextQuestion.id in previousQuestion:
                    nextQuestion = questionsQuery[randomIndex - 1]

                return jsonify(
                    {
                        "success": True,
                        "question": {
                            "answer": nextQuestion.answer,
                            "category": nextQuestion.category,
                            "difficulty": nextQuestion.difficulty,
                            "id": nextQuestion.id,
                            "question": nextQuestion.question,
                        },
                        "previousQuestions": previousQuestion,
                    }
                )

        except:

            abort(422)

    """
    @TODO:
    Create error handlers for all expected errors
    including 404 and 422.
    """

    @app.errorhandler(400)
    def bad_request_error(error):
        return jsonify({"success": False, "error": 400, "message": "bad request"}), 400

    @app.errorhandler(404)
    def not_found(error):
        return (
            jsonify({"success": False, "error": 404, "message": "resource not found"}),
            404,
        )

    @app.errorhandler(405)
    def not_found(error):
        return (
            jsonify({"success": False, "error": 405, "message": "method not allowed"}),
            405,
        )

    @app.errorhandler(422)
    def unprocessable(error):
        return (
            jsonify({"success": False, "error": 422, "message": "unprocessable"}),
            422,
        )

    @app.errorhandler(500)
    def internal_server_error(error):
        return (
            jsonify(
                {"success": False, "error": 500, "message": "internal server error"}
            ),
            500,
        )

    return app
