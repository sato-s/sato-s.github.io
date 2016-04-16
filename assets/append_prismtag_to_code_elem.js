/**
 * Created by sato on 16/04/17.
 */

var list = document.getElementsByTagName("code")

for (var i = 0; i< list.length;i++){
    if(list[i].className==false) {
        list[i].className = 'language-markup';
    }
}


var list = document.getElementsByTagName("pre")

for (var i = 0; i< list.length;i++){
    if(list[i].className==false) {
        list[i].className = 'line-numbers';
    }
}
