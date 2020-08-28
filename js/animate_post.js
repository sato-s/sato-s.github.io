function TickText(dom) {
  this.dom = dom;
  this.text = this.dom.innerText;
  this.dom.innerText = '';

  this.i = 1;

}

TickText.prototype.tick = function(){
}

$('.post-title').each(function(i,elem){
  TickText(elem);
  // console.log(elem)
  // console.log(i)
})
// anime({
//   targets: '.post-title',
//   borderColor: '#1A0',
//   easing: 'linear',
//   // borderRadius: ['0%', '50%'],
// });
// anime({
//   targets: '.post-title',
//   translateX: 250
// });
