import React, { useState, useRef, useEffect } from "react";
import { MotionConfig, motion } from "framer-motion";
import {
    Send,
    Download,
    User,
    Settings,
    MessageCircle,
    Zap,
} from "lucide-react";

export default function CampusChatbot() {
    const [messages, setMessages] = useState([
        {
            id: 1,
            from: "bot",
            text: "Hi! I'm Campusly — your campus assistant.",
        },
    ]);
    const [input, setInput] = useState("");
    const [loading, setLoading] = useState(false);
    const [connected, setConnected] = useState(true);
    const msgRef = useRef(null);

    useEffect(() => {
        if (msgRef.current) {
            msgRef.current.scrollTop = msgRef.current.scrollHeight;
        }
    }, [messages, loading]);

    const sendMessage = async (text) => {
        if (!text.trim()) return;

        const userMsg = { id: Date.now(), from: "user", text: text.trim() };
        setMessages((m) => [...m, userMsg]);
        setInput("");
        setLoading(true);

        try {
            const res = await fetch("http://localhost:5000/chat", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ query: text }),
            });

            if (!res.ok) throw new Error("Network error");

            const data = await res.json();
            const botReply = data.response || "Sorry — no response.";

            setMessages((m) => [
                ...m,
                { id: Date.now() + 1, from: "bot", text: botReply },
            ]);
        } catch (err) {
            console.error(err);
            setMessages((m) => [
                ...m,
                {
                    id: Date.now() + 2,
                    from: "bot",
                    text: "Sorry — something went wrong. Try again later.",
                },
            ]);
            setConnected(false);
        } finally {
            setLoading(false);
        }
    };

    const quickPrompts = [
        "Library hours",
        "Today's campus events",
        "How to register for courses",
        "Report a facility issue",
    ];

    return (
        <MotionConfig transition={{ duration: 0.25 }}>
            <div className="min-h-screen bg-gray-50 flex items-center justify-center p-6">
                <div className="max-w-6xl w-full grid grid-cols-1 lg:grid-cols-3 gap-6">
                    {/* Sidebar */}
                    <aside className="lg:col-span-1 bg-white rounded-2xl shadow-md p-5 flex flex-col gap-4">
                        <div className="flex items-center justify-between">
                            <div className="flex items-center gap-3">
                                <div className="bg-gradient-to-tr from-indigo-500 to-purple-500 text-white rounded-full p-2">
                                    <Zap size={18} />
                                </div>
                                <div>
                                    <h3 className="text-lg font-semibold">
                                        Campusly
                                    </h3>
                                    <p className="text-xs text-gray-500">
                                        AI-Powered Campus Assistant
                                    </p>
                                </div>
                            </div>
                            <div className="flex items-center gap-2">
                                <button
                                    className="p-2 rounded-md hover:bg-gray-100"
                                    title="Profile"
                                >
                                    <User size={16} />
                                </button>
                                <span
                                    className={`p-2 rounded-md ${
                                        connected
                                            ? "text-green-600"
                                            : "text-red-500"
                                    }`}
                                    title="Connection status"
                                >
                                    {connected ? "Online" : "Offline"}
                                </span>
                            </div>
                        </div>

                        {/* Quick Actions */}
                        <div className="mt-2">
                            <h4 className="text-sm font-medium text-gray-700">
                                Quick Actions
                            </h4>
                            <div className="mt-3 flex flex-col gap-2">
                                {quickPrompts.map((prompt, idx) => (
                                    <button
                                        key={idx}
                                        onClick={() => sendMessage(prompt)}
                                        className="text-sm bg-indigo-50 hover:bg-indigo-100 text-indigo-700 rounded-lg px-3 py-2 text-left"
                                    >
                                        {prompt}
                                    </button>
                                ))}
                            </div>
                        </div>

                        {/* Resources */}
                        <div className="mt-auto">
                            <h4 className="text-sm font-medium text-gray-700">
                                Campus Resources
                            </h4>
                            <ul className="mt-2 text-sm text-gray-600 space-y-2">
                                <li>IT Support — it-support@vit.ac.in</li>
                                <li>Health Center (24/7) — 220</li>
                                <li>Security (24/7) — 199</li>
                            </ul>

                            <div className="mt-4 flex gap-2">
                                <button className="flex-1 inline-flex items-center justify-center gap-2 rounded-lg border px-3 py-2 text-sm hover:bg-gray-50">
                                    <Download size={16} />
                                    Export Transcript
                                </button>
                                <button className="inline-flex items-center gap-2 rounded-lg bg-indigo-600 text-white px-3 py-2 text-sm hover:bg-indigo-700">
                                    <Settings size={16} />
                                    Settings
                                </button>
                            </div>
                        </div>
                    </aside>

                    {/* Chat Area */}
                    <main className="lg:col-span-2 bg-white rounded-2xl shadow-lg p-6 flex flex-col">
                        <div className="flex items-center justify-between mb-4">
                            <div className="flex items-center gap-3">
                                <MessageCircle size={20} />
                                <h2 className="text-xl font-semibold">
                                    Ask Campusly
                                </h2>
                            </div>
                        </div>

                        {/* Messages */}
                        <div
                            ref={msgRef}
                            className="flex-1 overflow-auto p-4 border border-gray-100 rounded-xl mb-4"
                            style={{ minHeight: 220 }}
                        >
                            <div className="space-y-3">
                                {messages.map((m) => (
                                    <motion.div
                                        key={m.id}
                                        initial={{ opacity: 0, y: 6 }}
                                        animate={{ opacity: 1, y: 0 }}
                                        className={`max-w-3xl ${
                                            m.from === "user"
                                                ? "ml-auto text-right"
                                                : "mr-auto text-left"
                                        }`}
                                    >
                                        <div
                                            className={`inline-block px-4 py-2 rounded-2xl ${
                                                m.from === "user"
                                                    ? "bg-indigo-600 text-white"
                                                    : "bg-gray-100 text-gray-800"
                                            }`}
                                        >
                                            {}
                                            <p className="text-sm leading-relaxed">
                                                {m.text
                                                    .split("\n")
                                                    .map((line, idx) => (
                                                        <React.Fragment
                                                            key={idx}
                                                        >
                                                            {line}
                                                            <br />
                                                        </React.Fragment>
                                                    ))}
                                            </p>

                                            <div className="text-[10px] text-gray-400 mt-1">
                                                {m.from === "user"
                                                    ? "You"
                                                    : "Campusly"}
                                            </div>
                                        </div>
                                    </motion.div>
                                ))}
                                {loading && (
                                    <div className="flex items-center space-x-2">
                                        <div className="h-8 w-8 rounded-full bg-indigo-100 animate-pulse" />
                                        <div className="text-sm text-gray-500">
                                            Campusly is typing...
                                        </div>
                                    </div>
                                )}
                            </div>
                        </div>

                        {/* Input */}
                        <form
                            onSubmit={(e) => {
                                e.preventDefault();
                                sendMessage(input);
                            }}
                            className="flex items-center gap-3"
                        >
                            <div className="flex-1 relative">
                                <input
                                    aria-label="Type your message"
                                    value={input}
                                    onChange={(e) => setInput(e.target.value)}
                                    className="w-full rounded-xl border px-4 py-3 pr-32 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-200"
                                    placeholder="Ask about library hours, events, or campus services..."
                                />
                            </div>

                            <div className="flex items-center gap-2">
                                <button
                                    type="submit"
                                    disabled={loading}
                                    className="inline-flex items-center gap-2 bg-indigo-600 text-white px-4 py-3 rounded-xl hover:bg-indigo-700 disabled:opacity-60"
                                >
                                    <Send size={16} />
                                    <span className="text-sm">Send</span>
                                </button>
                            </div>
                        </form>
                    </main>
                </div>
            </div>
        </MotionConfig>
    );
}
