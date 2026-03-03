"use strict";
var __spreadArray = (this && this.__spreadArray) || function (to, from, pack) {
    if (pack || arguments.length === 2) for (var i = 0, l = from.length, ar; i < l; i++) {
        if (ar || !(i in from)) {
            if (!ar) ar = Array.prototype.slice.call(from, 0, i);
            ar[i] = from[i];
        }
    }
    return to.concat(ar || Array.prototype.slice.call(from));
};
Object.defineProperty(exports, "__esModule", { value: true });
var react_1 = require("react");
var useUser_1 = require("../../../hooks/useUser");
var useApi_1 = require("../../../hooks/useApi");
var api_1 = require("../../../services/api");
var Card_1 = require("../../../components/ui/Card");
var Button_1 = require("../../../components/ui/Button");
var Badge_1 = require("../../../components/ui/Badge");
var lucide_react_1 = require("lucide-react");
var react_hot_toast_1 = require("react-hot-toast");
var QuizComponent = function () {
    var addXp = (0, useUser_1.useUser)().addXp;
    var _a = (0, useApi_1.useApi)(), loading = _a.loading, execute = _a.execute;
    var _b = (0, react_1.useState)(null), quiz = _b[0], setQuiz = _b[1];
    var _c = (0, react_1.useState)(0), currentQuestion = _c[0], setCurrentQuestion = _c[1];
    var _d = (0, react_1.useState)([]), answers = _d[0], setAnswers = _d[1];
    var _e = (0, react_1.useState)(false), showResults = _e[0], setShowResults = _e[1];
    var _f = (0, react_1.useState)(0), score = _f[0], setScore = _f[1];
    (0, react_1.useEffect)(function () {
        generateNewQuiz();
    }, []);
    var generateNewQuiz = function () {
        execute(function () { return api_1.apiService.generateQuiz(); }, function (response) {
            setQuiz(response);
            setCurrentQuestion(0);
            setAnswers([]);
            setShowResults(false);
            setScore(0);
        });
    };
    var handleAnswer = function (selectedAnswer) {
        var newAnswers = __spreadArray([], answers, true);
        newAnswers[currentQuestion] = selectedAnswer;
        setAnswers(newAnswers);
    };
    var nextQuestion = function () {
        if (currentQuestion < quiz.questions.length - 1) {
            setCurrentQuestion(currentQuestion + 1);
        }
        else {
            submitQuiz();
        }
    };
    var previousQuestion = function () {
        if (currentQuestion > 0) {
            setCurrentQuestion(currentQuestion - 1);
        }
    };
    var submitQuiz = function () {
        if (!quiz)
            return;
        var submissions = answers.map(function (answer, index) { return ({
            questionId: index,
            selectedAnswer: answer,
        }); });
        execute(function () { return api_1.apiService.submitQuiz(submissions); }, function (result) {
            var correctCount = answers.filter(function (answer, index) {
                return answer === quiz.questions[index].correctAnswer;
            }).length;
            setScore(correctCount);
            setShowResults(true);
            addXp(result.xpGained || 25); // Added fallback value
            react_hot_toast_1.default.success("Quiz completed! Score: ".concat(correctCount, "/").concat(quiz.questions.length, " | +").concat(result.xpGained || 25, " XP"));
        });
    };
    if (!quiz) {
        return (<div className="space-y-6">
                <div>
                    <h2 className="text-3xl font-bold text-primary-900 mb-2">Quiz Mode</h2>
                    <p className="text-primary-600">
                        Test your knowledge with AI-generated questions from your documents
                    </p>
                </div>

                <Card_1.default variant="glass" className="p-8">
                    <div className="flex items-center justify-center min-h-[300px]">
                        {loading ? (<div className="animate-spin rounded-full h-12 w-12 border-b-2 border-accent-500"></div>) : (<div className="text-center">
                                <lucide_react_1.Brain className="h-16 w-16 text-primary-400 mx-auto mb-4"/>
                                <p className="text-primary-600 mb-4">Loading quiz questions...</p>
                                <Button_1.default onClick={generateNewQuiz} loading={loading}>
                                    Generate Quiz
                                </Button_1.default>
                            </div>)}
                    </div>
                </Card_1.default>
            </div>);
    }
    if (showResults) {
        return (<div className="space-y-6">
                <div>
                    <h2 className="text-3xl font-bold text-primary-900 mb-2">Quiz Results</h2>
                    <p className="text-primary-600">
                        Here's how you performed on the quiz
                    </p>
                </div>

                <Card_1.default variant="glass" className="p-8">
                    <div className="text-center mb-6">
                        <div className="w-24 h-24 bg-gradient-to-br from-accent-500 to-accent-600 rounded-full flex items-center justify-center mx-auto mb-4">
                            <lucide_react_1.Trophy className="h-12 w-12 text-white"/>
                        </div>

                        <h3 className="text-2xl font-bold text-primary-900 mb-2">
                            Score: {score}/{quiz.questions.length}
                        </h3>

                        <Badge_1.default variant="success" className="mb-4">
                            {((score / quiz.questions.length) * 100).toFixed(0)}% Correct
                        </Badge_1.default>

                        <p className="text-primary-600">
                            {score === quiz.questions.length
                ? "Perfect score! You're a master!"
                : score >= quiz.questions.length / 2
                    ? "Good job! Keep learning!"
                    : "Keep practicing! You'll get better!"}
                        </p>
                    </div>

                    <div className="space-y-3 mb-6">
                        {quiz.questions.map(function (question, index) { return (<div key={index} className={"\n                  p-4 rounded-lg border-2\n                  ".concat(answers[index] === question.correctAnswer
                    ? 'border-success bg-success/10'
                    : 'border-danger bg-danger/10', "\n                ")}>
                                <div className="flex items-center justify-between mb-2">
                                    <p className="font-medium text-primary-900">
                                        Question {index + 1}
                                    </p>
                                    {answers[index] === question.correctAnswer ? (<lucide_react_1.CheckCircle className="h-5 w-5 text-success"/>) : (<span className="text-danger text-sm font-medium">
                                            Correct: {question.options[question.correctAnswer]}
                                        </span>)}
                                </div>

                                <p className="text-primary-600 text-sm mb-2">{question.question}</p>

                                <p className="text-primary-700 text-sm">
                                    Your answer: {answers[index] !== undefined ? question.options[answers[index]] : 'Not answered'}
                                </p>
                            </div>); })}
                    </div>

                    <div className="flex justify-center space-x-4">
                        <Button_1.default onClick={generateNewQuiz} variant="accent">
                            <lucide_react_1.RotateCcw className="h-4 w-4 mr-2"/>
                            New Quiz
                        </Button_1.default>
                    </div>
                </Card_1.default>
            </div>);
    }
    var currentQ = quiz.questions[currentQuestion];
    var progress = ((currentQuestion + 1) / quiz.questions.length) * 100;
    return (<div className="space-y-6">
            <div>
                <h2 className="text-3xl font-bold text-primary-900 mb-2">Quiz Mode</h2>
                <p className="text-primary-600">
                    Test your knowledge with questions from your documents
                </p>
            </div>

            {/* Progress Bar */}
            <Card_1.default variant="glass" className="p-4">
                <div className="flex items-center justify-between mb-2">
                    <div className="flex items-center space-x-2">
                        <lucide_react_1.Brain className="h-5 w-5 text-accent-500"/>
                        <span className="text-primary-900 font-medium">
                            Question {currentQuestion + 1} of {quiz.questions.length}
                        </span>
                    </div>

                    <Badge_1.default variant="accent">
                        {Math.round(progress)}% Complete
                    </Badge_1.default>
                </div>

                <div className="w-full h-3 bg-primary-200 rounded-full overflow-hidden">
                    <div className="h-full bg-gradient-to-r from-accent-500 to-accent-600 transition-all duration-500" style={{ width: "".concat(progress, "%") }}/>
                </div>
            </Card_1.default>

            {/* Current Question */}
            <Card_1.default variant="glass" className="p-6">
                <div className="mb-6">
                    <div className="flex items-center space-x-2 mb-4">
                        <lucide_react_1.Clock className="h-5 w-5 text-primary-600"/>
                        <span className="text-primary-600 font-medium">
                            Context from your documents
                        </span>
                    </div>

                    <div className="p-4 rounded-lg bg-primary-100/30 mb-6">
                        <p className="text-primary-700 italic">
                            "{quiz.contextUsed}"
                        </p>
                    </div>
                </div>

                <h3 className="text-xl font-semibold text-primary-900 mb-6">
                    {currentQ.question}
                </h3>

                <div className="space-y-3 mb-8">
                    {currentQ.options.map(function (option, index) { return (<button key={index} onClick={function () { return handleAnswer(index); }} className={"\n                w-full text-left p-4 rounded-lg border-2 transition-all duration-200\n                ".concat(answers[currentQuestion] === index
                ? 'border-accent-500 bg-accent-500/10'
                : 'border-primary-300 hover:border-primary-400 hover:bg-primary-100/30', "\n              ")}>
                            <div className="flex items-center space-x-3">
                                <div className={"\n                  w-6 h-6 rounded-full border-2 flex items-center justify-center\n                  ".concat(answers[currentQuestion] === index
                ? 'border-accent-500 bg-accent-500'
                : 'border-primary-400', "\n                ")}>
                                    {answers[currentQuestion] === index && (<div className="w-2 h-2 bg-white rounded-full"/>)}
                                </div>
                                <span className="text-primary-900">{option}</span>
                            </div>
                        </button>); })}
                </div>

                <div className="flex justify-between">
                    <Button_1.default variant="secondary" onClick={previousQuestion} disabled={currentQuestion === 0}>
                        Previous
                    </Button_1.default>

                    <Button_1.default variant="accent" onClick={nextQuestion} disabled={answers[currentQuestion] === undefined}>
                        {currentQuestion === quiz.questions.length - 1 ? 'Submit Quiz' : 'Next'}
                    </Button_1.default>
                </div>
            </Card_1.default>

            <Card_1.default variant="glass" className="p-4">
                <div className="flex items-center justify-between">
                    <p className="text-primary-600">
                        Complete the quiz to earn up to 50 XP
                    </p>
                    <Badge_1.default variant="accent">+50 XP</Badge_1.default>
                </div>
            </Card_1.default>
        </div>);
};
exports.default = QuizComponent;
