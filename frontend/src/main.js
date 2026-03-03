"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var react_1 = require("react");
var client_1 = require("react-dom/client");
var react_router_dom_1 = require("react-router-dom");
var react_hot_toast_1 = require("react-hot-toast");
var App_1 = require("./App");
require("./index.css");
client_1.default.createRoot(document.getElementById('root')).render(<react_1.default.StrictMode>
        <react_router_dom_1.BrowserRouter>
            <App_1.default />
            <react_hot_toast_1.Toaster position="top-right" toastOptions={{
        duration: 4000,
        style: {
            background: '#1e293b',
            color: '#f1f5f9',
            border: '1px solid #334155',
        },
    }}/>
        </react_router_dom_1.BrowserRouter>
    </react_1.default.StrictMode>);
