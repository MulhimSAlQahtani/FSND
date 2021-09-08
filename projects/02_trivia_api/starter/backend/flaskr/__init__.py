import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

def paginate_questions(request, selection):
    page = request.args.get("page", 1, type=int)
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE

    questions = [question.format() for question in selection]
    current_questions = questions[start:end]
    return current_questions

def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  setup_db(app)
  
  
    # Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
    CORS(app, resources={"r/*": {"origins": "*"}})

  
    # Use the after_request decorator to set Access-Control-Allow
    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization, true')
        response.headers.add('Access-Control-Allow-Methods', 'GET, POST, PATCH, DELETE, OPTIONS')
        return response

 
    #Create an endpoint to handle GET requests for all available categories.
    @app.route("/categories", methods=["GET"])
    def get_categories():
        categories = {
            category.id: category.type for category in Category.query.all()}

        return jsonify({"success": True, "categories": categories}), 200

  
    #Create an endpoint to handle GET requests for questions, 
    #including pagination (every 10 questions). 
 
    @app.route("/questions", methods=["GET"])
    def get_questions():
        selection = Question.query.all()
        current_questions = paginate_questions(request, selection)

        if len(current_questions) == 0:
            abort(404)

        return (
            jsonify(
                {
                    "success": True,
                    "questions": current_questions,
                    "total_questions": len(selection)
                }
            ),
            200,
        )

 
    #Create an endpoint to DELETE question using a question ID. 

    @app.route("/questions/<int:question_id>", methods=["DELETE"])
    def delete_question(question_id):
        try:
            question = Question.query.get_or_404(question_id)
            question.delete()
        except BaseException:
            abort(422)

        return (
            jsonify(
                {"success": True, "message": "Question deleted successfully"}
            ),
            200,
        )

    # Create an endpoint to POST a new question, 
    # which will require the question and answer text, 
    # category, and difficulty score.
    @app.route("/questions", methods=["POST"])
    def create_question():
        data = request.get_json()
        question = (data.get("question"),)
        answer = (data.get("answer"),)
        category = (data.get("category"),)
        difficulty = data.get("difficulty")

        if not(question and answer and category and difficulty):
            abort(400)

        try:
            question = Question(
                question=question,
                answer=answer,
                category=category,
                difficulty=difficulty,
            )
            question.insert()
        except BaseException:
            abort(400)

        return jsonify({"success": True, "question": question.format()}), 200

 
    # Create a POST endpoint to get questions based on a search term. 
    # It should return any questions for whom the search term 
    # is a substring of the question. 
    @app.route("/questions/search", methods=["POST"])
    def search_question():
        data = request.get_json()
        search_term = data.get("searchTerm")
        search_results = Question.query.filter(
            Question.question.ilike(f"%{search_term}%")
        ).all()
        questions = paginate_questions(request, search_results)
        num_of_questions = len(questions)

        if num_of_questions == 0:
            abort(404)

        return (
            jsonify(
                {
                    "success": True,
                    "questions": questions,
                    "total_questions": num_of_questions,
                    "current_category": None,
                }
            ),
            200,
        )

    #Create a GET endpoint to get questions based on category. 
    @app.route("/categories/<int:category_id>/questions", methods=["GET"])
    def get_questions_by_category(category_id):
        selection = Question.query.filter_by(category=category_id).all()
        questions = paginate_questions(request, selection)
        num_of_questions = len(selection)

        if num_of_questions == 0:
            abort(404)

        return (
            jsonify(
                {
                    "success": True,
                    "questions": questions,
                    "total_questions": num_of_questions,
                    "current_category": category_id,
                }
            ),
            200,
        )

    # Create a POST endpoint to get questions to play the quiz. 
    # This endpoint should take category and previous question parameters 
    # and return a random questions within the given category, 
    # if provided, and that is not one of the previous questions. 
    @app.route("/quizzes", methods=["POST"])
    def get_quizzes():
        data = request.get_json()
        previous_questions = data.get("previous_questions")
        quiz_category = data.get("quiz_category")
        quiz_category_id = int(quiz_category["id"])

        question = Question.query.filter(
            Question.id.notin_(previous_questions)
        )

        # quiz category id is 0 if all is selected and therefore false
        if quiz_category_id:
            question = question.filter_by(category=quiz_category_id)

        # limit result to only one question
        question = question.first().format()

        return jsonify({"success": True, "question": question, }), 200


    #Create error handlers for all expected errors 
    @app.errorhandler(400)
    def bad_request(error):
        return (
            jsonify(
                {"success": False, "error": 400, "message": "Bad Request"}
            ),
            400,
        )

    @app.errorhandler(404)
    def not_found(error):
        return (
            jsonify({"success": False, "error": 404, "message": "Not Found"}),
            404,
        )

    @app.errorhandler(405)
    def method_not_allowed(error):
        return (
            jsonify(
                {
                    "success": False,
                    "error": 405,
                    "message": "Method Not Allowed",
                }
            ),
            405,
        )

    @app.errorhandler(422)
    def uprocessible_entity(error):
        return (
            jsonify(
                {
                    "success": False,
                    "error": 422,
                    "message": "Unprocessible Entity",
                }
            ),
            422,
        )

    @app.errorhandler(500)
    def internal_server_error(error):
        return (
            jsonify(
                {
                    "success": False,
                    "error": 500,
                    "message": "Internal Server Error",
                }
            ),
            500,
        )
  
  return app

    