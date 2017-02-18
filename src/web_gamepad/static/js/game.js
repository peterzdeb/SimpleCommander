var FPS = 60;
var KEYCODE_UP = 38;
var KEYCODE_DOWN = 40;
var KEYCODE_LEFT = 37;
var KEYCODE_RIGHT = 39;
var KEYCODE_SPACE = 32;

var hero;                  //the actual hero

function GameController(canvas) {
    "use strict";

    this.hero = null;
    this.units = {};
    this.speed = false;
    this.canvas = canvas;
    this.socket = null;

    this.activeKeys = {};

    /*global SocketHandler */
    var socket = SocketHandler,
        controller = this;
    /*global document */
    document.onkeydown = function (e) {
        controller.handleKeyDown(e);
    };

    document.onkeyup = function (e) {
        controller.handleKeyUp(e);
    };

    this.createConnection = function (name) {
        this.socket = socket(this, name);
    };

    this.sendToServer = function (keyCode, action, keyTitle) {
        var data = {'code': keyCode, 'type': action, 'action': keyTitle};
        data = JSON.stringify(data);
        this.socket.send(data);
    };


    this.onData = function (event) {
        var key, answer = JSON.parse(event.data);
        for (key in answer) {
            switch (key) {
                case 'init':
                    this.start(answer.init);
                    break;
                case 'error':
                    this.error(answer.error);
                    break;
                case 'update':
                    this.updateUnit(answer.update);
                    break;
                case 'delete':
                    this.killUnit(answer.delete);
                    break;
                case 'update_life':
                    this.updateLife(answer.update_life);
                    break;
            }
        }

    };

    this.error = function (error) {
        console.log(error);
    };

    this.start = function (init) {

        //reset key presses
        this.leftPress = this.rightPress = this.upPress = this.downPress = this.spascePress = false;

        //start game timer
        if (!createjs.Ticker.hasEventListener("tick")) {
            createjs.Ticker.setFPS(FPS);
            var controller = this;
        }
    };

    this.updateTableScorecards = function(){
        var statuses = [];
        for (var key in this.activeKeys) {
            if (this.activeKeys[key]) {
                statuses.push(key);
            }
        }

        var lifeCount = document.getElementById('hero-lifes');
        lifeCount.textContent = statuses;
    };

    this.getKeyTitle = function(code) {
        var keyTitle = '';
        switch (code) {
            case KEYCODE_LEFT:
                keyTitle = 'left';
                break;
            case KEYCODE_RIGHT:
                keyTitle = 'right';
                break;
            case KEYCODE_UP:
                //TODO: What is the meaning of `speed` as boolean. Non sense to me
                keyTitle = 'up';
                break;
            case KEYCODE_DOWN:
                keyTitle = 'down';
                break;
            case KEYCODE_SPACE:
                keyTitle = 'space';
                break;
        }
        return keyTitle;
    };

    this.handleKeyDown = function (e) {
        //cross browser issues exist
        if (!e) {
            var e = window.event;
        }

        var keyTitle = this.getKeyTitle(e.keyCode);

        if (!this.activeKeys[e.keyCode]){
            this.activeKeys[e.keyCode] = true;
            this.sendToServer(e.keyCode, 'key_down', keyTitle);
            this.updateTableScorecards();
        }

    };

    this.handleKeyUp = function (e) {
        //cross browser issues exist
        if (!e) {
            var e = window.event;
        }
        var keyTitle = this.getKeyTitle(e.keyCode);

        if (this.activeKeys[e.keyCode]){
            this.activeKeys[e.keyCode] = false;
            this.sendToServer(e.keyCode, 'key_up', keyTitle);
            this.updateTableScorecards();
        }

    };
}

window.onload = function() {
    var canvas = document.getElementById("gameCanvas");
    var theGame = new GameController(canvas);
    theGame.createConnection(name);
};
