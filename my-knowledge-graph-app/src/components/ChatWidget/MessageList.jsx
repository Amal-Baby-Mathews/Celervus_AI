import React, { useState, useMemo, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { ChevronDown, CheckCircle } from 'lucide-react';

const BotMessageContent = ({ messageText, isStreaming }) => {
  const [isThinkingExpanded, setIsThinkingExpanded] = useState(false);
  const [accumulatedText, setAccumulatedText] = useState('');

  // Accumulate tokens as they come from the backend
  useEffect(() => {
    if (isStreaming) {
      setAccumulatedText(prev => prev + (messageText || ''));
    } else {
      setAccumulatedText(messageText || '');
    }
  }, [messageText, isStreaming]);

  const { thinkingLines, answerLines, isStructured } = useMemo(() => {
    if (!accumulatedText) {
      return { thinkingLines: [], answerLines: [], isStructured: false };
    }

    const lines = accumulatedText.split('\n').filter(line => line.trim() !== '');
    const thinking = [];
    const answer = [];
    let answerStarted = false;
    const answerPrefixes = ["Answer:", "Final answer:", "Partial answer:"];
    let foundAnswerPrefix = false;

    for (const line of lines) {
      const trimmedLine = line.trim();
      let isPrefixMatch = false;

      for (const prefix of answerPrefixes) {
        if (trimmedLine.startsWith(prefix)) {
          answerStarted = true;
          foundAnswerPrefix = true;
          const answerContent = trimmedLine.substring(prefix.length).trim();
          if (answerContent) {
            answer.push(answerContent);
          }
          isPrefixMatch = true;
          break;
        }
      }

      if (!isPrefixMatch) {
        if (answerStarted) {
          answer.push(trimmedLine);
        } else {
          thinking.push(trimmedLine);
        }
      }
    }

    const structured = foundAnswerPrefix || thinking.length > 0;
    if (!foundAnswerPrefix && thinking.length > 0) {
      return { thinkingLines: [], answerLines: thinking, isStructured: false };
    }

    return { thinkingLines: thinking, answerLines: answer, isStructured: structured };
  }, [accumulatedText]);

  if (!isStructured && answerLines.length === 0) {
    return (
      <p className="whitespace-pre-wrap break-words">
        {accumulatedText || <span className="italic opacity-75">Typing...</span>}
      </p>
    );
  }

  return (
    <div>
      {/* Thinking Section (Expandable) */}
      {thinkingLines.length > 0 && (
        <div className="mb-2 border border-gray-300 dark:border-gray-600 rounded-md overflow-hidden">
          <button
            onClick={() => setIsThinkingExpanded(!isThinkingExpanded)}
            className={`w-full flex justify-between items-center p-1.5 px-2 text-xs text-gray-500 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-600/50 transition-colors ${isThinkingExpanded ? 'rounded-t-md' : 'rounded-md'}`}
          >
            <span>Thinking Process ({thinkingLines.length} steps)</span>
            <ChevronDown
              size={14}
              className={`transform transition-transform duration-200 ${isThinkingExpanded ? 'rotate-180' : ''}`}
            />
          </button>
          <AnimatePresence>
            {isThinkingExpanded && (
              <motion.div
                initial={{ height: 0, opacity: 0 }}
                animate={{ height: 'auto', opacity: 1 }}
                exit={{ height: 0, opacity: 0 }}
                transition={{ duration: 0.25, ease: 'easeInOut' }}
                className="overflow-hidden border-t border-gray-300 dark:border-gray-600"
              >
                <pre className="p-2 text-xs text-gray-600 dark:text-gray-400 whitespace-pre-wrap break-words bg-gray-50 dark:bg-gray-800/40">
                  {thinkingLines.join('\n')}
                </pre>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      )}

      {/* Answer Section (Highlighted) */}
      {answerLines.length > 0 && (
        <div className="bg-emerald-50 dark:bg-emerald-900/30 p-2.5 rounded-md border border-emerald-200 dark:border-emerald-700/50 shadow-sm">
          <div className="flex items-start text-emerald-700 dark:text-emerald-300 mb-1">
            <CheckCircle size={16} className="mr-1.5 flex-shrink-0 mt-0.5" />
            <h5 className="text-sm font-semibold">Response</h5>
          </div>
          <p className="whitespace-pre-wrap break-words text-sm text-gray-800 dark:text-gray-100 pl-5">
            {answerLines.join('\n')}
          </p>
        </div>
      )}

      {/* Fallback for unstructured streaming text */}
      {thinkingLines.length === 0 && answerLines.length === 0 && accumulatedText && isStructured && (
        <p className="whitespace-pre-wrap break-words">{accumulatedText}</p>
      )}
    </div>
  );
};


function MessageList({ messages, isStreaming }) {
  return (
    <>
      {messages.map((msg) => (
        <div
          key={msg.id}
          className={`flex mb-3 ${msg.sender === 'user' ? 'justify-end' : 'justify-start'}`}
        >
          <div
            className={`max-w-[80%] p-3 rounded-lg shadow-sm ${
              msg.sender === 'user'
                ? 'bg-blue-500 text-white'
                : msg.error
                ? 'bg-red-100 dark:bg-red-900/50 text-red-700 dark:text-red-300 border border-red-300 dark:border-red-700'
                : 'bg-gray-100 dark:bg-gray-700/60 text-gray-800 dark:text-gray-100 border border-gray-200 dark:border-gray-600/80'
            }`}
          >
            {msg.sender === 'user' ? (
              <p className="whitespace-pre-wrap break-words">{msg.text}</p>
            ) : msg.error ? (
              <p className="whitespace-pre-wrap break-words">{msg.text}</p>
            ) : (
              <BotMessageContent
                messageText={msg.text}
                isStreaming={isStreaming && msg.id === messages[messages.length - 1].id}
              />
            )}
          </div>
        </div>
      ))}
    </>
  );
}

export default MessageList;