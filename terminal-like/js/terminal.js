function terminalLike(options) {
  "use strict"
  // argument handling
  if (typeof options === 'undefined' ) options = {};
  if (typeof options.prompt === 'undefined') options.prompt = '[user@localhost ~]$';
  if (typeof options.title === 'undefined') options.title = 'Terminal ~ '

  var terminals = document.getElementsByClassName('terminal-like');
  var new_terminals = [];
  [].forEach.call(terminals, function (terminal,index) {
    // window to replace original element
    var new_terminal  = document.createElement('div');
    new_terminal.className = 'terminal-like';

    // terminal title
    var title = document.createElement('span');
    title.innerText = options.title;
    title.className = 'terminal-like-title';
    // terminal buttons
    var buttons = document.createElement('span');
    buttons.className = 'terminal-like-buttons';
    var closeButton = document.createElement('span');
    closeButton.className = 'terminal-like-button';
    closeButton.innerHTML = '&times;';
    var minimizeButton = document.createElement('span')
    minimizeButton.innerHTML = '&horbar;';
    minimizeButton.className = 'terminal-like-button';
    var maximizeButton = document.createElement('span')
    maximizeButton.innerHTML = '&Square;';
    maximizeButton.className = 'terminal-like-button';
    
    buttons.appendChild(minimizeButton);
    buttons.appendChild(maximizeButton);
    buttons.appendChild(closeButton);

    // terminal header
    var titleBar = document.createElement('div');
    titleBar.className='terminal-like-header';
    titleBar.appendChild(title);
    titleBar.appendChild(buttons);

    // terminal body
    // append prompt to text
    var prompt = '<span class="terminal-like-prompt">'+options.prompt+'</span>';
    var text = terminal.textContent;
    text = 
      text.split('\n')
      .map( function(line)
        {return (prompt+'<span class="terminal-like-shell-body">'+line+'</span>')})
      .join('\n');

    var textArea = document.createElement('div');
    textArea.className = 'terminal-like-textArea';
    textArea.innerHTML= '<pre><code>'+text+'</code></pre>';

    new_terminal.appendChild(titleBar);
    new_terminal.appendChild(textArea);
    new_terminals[index] = new_terminal
  });

  [].forEach.call(terminals, function (terminal,index) {
    terminal.parentNode.replaceChild(new_terminals[index],terminal)
  });
}
