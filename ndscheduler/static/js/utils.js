require.config({
  paths: {
    'spin': 'vendor/spin',
    'noty': 'vendor/jquery.noty',
    'jquery': 'vendor/jquery'
  },

  shim: {
    'noty': {
      deps: ['jquery']
    }
  }
});

define(['spin', 'noty'], function(Spinner) {
  'use strict';

  /**
   * Starts a spinner.
   *
   * @param {String} parentDomId The parent element id for spinner.
   * @return {Spinner} object of Spinner
   */
  var startSpinner = function(parentDomId) {
    var opts = {
      lines: 13, // The number of lines to draw
      length: 20, // The length of each line
      width: 10, // The line thickness
      radius: 30, // The radius of the inner circle
      corners: 1, // Corner roundness (0..1)
      rotate: 0, // The rotation offset
      direction: 1, // 1: clockwise, -1: counterclockwise
      color: '#000', // #rgb or #rrggbb or array of colors
      speed: 1, // Rounds per second
      trail: 60, // Afterglow percentage
      shadow: false, // Whether to render a shadow
      hwaccel: false, // Whether to use hardware acceleration
      className: 'spinner', // The CSS class to assign to the spinner
      zIndex: 2e9, // The z-index (defaults to 2000000000)
      top: '150%', // Top position relative to parent
      left: '50%'  // Left position relative to parent
    };
    var spinner = new Spinner(opts).spin();
    $('#' + parentDomId).html(spinner.el);
    return spinner;
  };

  /**
   * Stops a spinner.
   *
   * @param {Spinner} spinner The spinner object to stop.
   */
  var stopSpinner = function(spinner) {
    spinner.stop();
  };

  /**
   * Display an error message.
   *
   * @param {String} msg Error message to display.
   */
  var alertError = function(msg) {
    noty({
      type: 'error',
      text: msg,
      timeout: 2000
    });
  };

  /**
   * Display a success message.
   *
   * @param {String} msg Success message to display.
   */
  var alertSuccess = function(msg) {
    noty({
      type: 'success',
      text: msg,
      timeout: 2000
    });
  };

  /**
   * Get json object of arguments of a task.
   *
   * @param {String} argsString Arguments passed to a task in json string.
   * @return {*} json object
   * @private
   */
  var getTaskArgs = function(argsString) {
    // argsString should be a json string
    if (argsString.trim() === '') {
      return [];
    }

    return JSON.parse(argsString);
  };

  /**
   * Get query parameter.
   *
   * @param {String} name query parameter name.
   * @return {String} value of that query parameter.
   */
  var getParameterByName = function(name) {
    var url = window.location.href;
    var results = new RegExp('[\\?&]' + name + '=([^&#]*)').exec(url);
    if (!results) {
      return undefined;
    }
    return results[1] || undefined;
  };

  /**
   * Public functions
   */
  return {
    startSpinner: startSpinner,
    stopSpinner: stopSpinner,

    alertSuccess: alertSuccess,
    alertError: alertError,

    getTaskArgs: getTaskArgs,
    getParameterByName: getParameterByName
  };
});
