import React, { useState } from "react";
import axios from "axios";
import { SpinnerDotted } from "spinners-react";
import { questionsList } from "./data/context";

function App() {
  const [question, setQuestion] = useState("");
  const [context, setContext] = useState("");
  const [answer, setAnswer] = useState(null);
  const [related, setRelated] = useState([]);
  const [suggestions, setSuggestions] = useState([]);
  const [error, setError] = useState("");
  const [isLoadingAnswers, setLoadingAnswers] = useState(false);
  const [expandedQuestionIndex, setExpandedQuestionIndex] = useState(-1);

  const getAnswers = async () => {
    if (question === null || question === "") {
      alert("Please enter your quetion");
      return;
    }
    try {
      setSuggestions([]);

      setLoadingAnswers(true);
      const response = await axios.post("http://localhost:5000/answer", {
        question,
        context,
      });

      if (response.data.related && response.data.related.length > 0) {
        setRelated(response.data.related);
      }

      if (response.data.answers && response.data.answers.length > 0) {
        // Find the answer with the highest score
        const highestScoreAnswer = response.data.answers.reduce(
          (max: any, answer: any) => (answer.score > max.score ? answer : max),
          response.data.answers[0]
        );
        setAnswer(highestScoreAnswer);
        setLoadingAnswers(false);
        setContext("");
      } else {
        setError("No answers found.");
        setAnswer(null);
        setLoadingAnswers(false);
        setContext("");
      }
    } catch (error) {
      setLoadingAnswers(false);
      setContext("");
      console.error(error);
    }
  };

  const toggleExpandQuestion = (index: any) => {
    if (expandedQuestionIndex === index) {
      setExpandedQuestionIndex(-1);
    } else {
      setExpandedQuestionIndex(index);
    }
  };

  const handleSuggestions = (e: any) => {
    const input = e.target.value;

    // Filter questions based on the input
    const filteredQuestions: any = questionsList
      .filter((q) => q.question.toLowerCase().includes(input.toLowerCase()))
      .slice(0, 5);

    setSuggestions(filteredQuestions);
  };

  return (
    <div
      className="bg-gray-100 min-h-screen flex items-center justify-center"
      onClick={() => {
        setSuggestions([]);
      }}
    >
      <div className="bg-white p-6 rounded-lg shadow-md w-full max-w-5xl">
        <h1 className="text-2xl font-semibold mb-2">
          Enter your question here
        </h1>
        <div className="flex items-center">
          <input
            type="text"
            placeholder="Your question"
            className="w-full p-3 mb-2 border rounded-lg outline-none"
            value={question}
            required={true}
            onChange={(e) => {
              if (e.target.value === "" || e.target.value == null) {
                setAnswer(null);
                setSuggestions([]);
                setContext("");
              }
              setQuestion(e.target.value);
              handleSuggestions(e);
            }}
          />

          <button
            onClick={getAnswers}
            className={`bg-blue-500 text-white p-3 mb-2 rounded-lg hover:bg-blue-600 cursor-pointer ml-2 ${
              isLoadingAnswers ? "opacity-50 pointer-events-none" : "" // Disable the button and change the cursor when isLoadingAnswers is true
            }`}
          >
            {isLoadingAnswers ? (
              <SpinnerDotted
                color="white"
                size={20}
                enabled={isLoadingAnswers}
              />
            ) : (
              "Submit"
            )}{" "}
            {/* Show "Loading..." text when isLoadingAnswers is true */}
          </button>
        </div>
        {suggestions.length > 0 && (
          <div className="absolute bg-white border rounded-lg mt-1 w-1/2 z-50">
            {suggestions.map((suggestion, index) => (
              <div
                key={index}
                className="p-2 cursor-pointer hover:bg-gray-100"
                onClick={() => {
                  setQuestion(suggestion["question"]);
                  setContext(suggestion["context"]);
                  setSuggestions([]);
                }}
              >
                {suggestion["question"]}
              </div>
            ))}
          </div>
        )}
        {answer && (
          <div className="mt-4">
            <h2 className="text-lg font-semibold mb-2">Answer</h2>
            <div className="mb-2">
              <div className="bg-blue-100 p-3 rounded-lg text-justify">
                {answer["answer"]}
              </div>
            </div>
          </div>
        )}
        {error !== "" && (
          <div className="mt-4">
            <div className="bg-yellow-100 p-3 rounded-lg">
              Sorry, no answers found for the given question.
            </div>
          </div>
        )}

        {related && related.length > 0 && (
          <div className="mt-10">
            <span className="text-2xl opacity-50">
              Most related questions for you
            </span>
            {related.map((relatedQues, rIndex) => (
              <div>
                <div key={rIndex} className="flex items-center mt-2">
                  <div
                    className="mr-2 cursor-pointer"
                    onClick={() => toggleExpandQuestion(rIndex)}
                  >
                    {expandedQuestionIndex === rIndex ? "-" : "+"}
                  </div>
                  <div
                    className="text-blue-600 cursor-pointer"
                    onClick={() => toggleExpandQuestion(rIndex)}
                  >
                    {relatedQues["question"]}
                  </div>
                </div>
                {expandedQuestionIndex === rIndex && (
                  <div className="bg-gray-200 p-3 rounded-lg mt-2 text-justify">
                    {relatedQues["answer"]}
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

export default App;
