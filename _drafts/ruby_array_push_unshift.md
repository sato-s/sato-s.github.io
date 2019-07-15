---
layout: post
title: RubyのArray#unshift速すぎる件と償却解析
date: '2019-03-06T00:00:00.000+09:00'
author: s sato
tags:
- ruby
- algorithm
---

https://stackoverflow.com/questions/8353026/what-is-the-run-time-of-shift-unshift-in-a-ruby-array
https://github.com/ruby/ruby/commit/fdbd3716781817c840544796d04a7d41b856d9f4
https://ja.wikipedia.org/wiki/%E5%84%9F%E5%8D%B4%E8%A7%A3%E6%9E%90
http://blade.nagaokaut.ac.jp/cgi-bin/scat.rb/ruby/ruby-dev/36734

プログラミング言語によって呼ばれ方はさまざまであるが、rubyにおいて`push`は
配列の最後尾にあらたな要素を付け足す処理を指す。   

```ruby
a = [1,2,3,4,5]
a.push('push')
puts a # => [1, 2, 3, 4, 5, 'push']
```

一方で`unshift`は、以下のように配列の先頭に要素を付け足す動作を指している。  

```ruby
a = [1,2,3,4,5]
a.unshift('unshift')
puts a # => ['unshift', 1, 2, 3, 4, 5]
```

rubyにおいて、Arrayは最初に要素数を宣言しなくても使用できるし、要素を追加すれば動的に勝手に拡張していってくれるものになっている。  



## unshiftの

少しパフォーマンスの気になるRubyのコードがあり、`Array#unshift`と`Array#push`のベンチマークと取ってみた。  

```ruby
a = []
t = Time.now
1_000_000.times{a.unshift(1)}
puts "unshift: #{Time.now - t}"

a = []
t = Time.now
1_000_000.times{a.push(1)}
puts "push: #{Time.now - t}"
```

実行結果は、`push`が0.09秒に対して、`unshift`が0.08秒だった。  

![array-push]({{ site.url }}/assets/array_push_double.svg)


| 言語                      | push  | unshift |
| :------:                  | :----:| :----:  |
| ruby (MRI 2.6.0)          | 0.09  | 0.08    |
| javascript (node v12.2.0) | 0.042 | 251.47  |
| python (c-python 3.7.2)   | 0.12  | 331.53  |


```
[5] pry(main)> a = []
=> []
[6] pry(main)> ObjectSpace.memsize_of(a)
=> 40
[7] pry(main)> ObjectSpace.memsize_of(a.unshift(1))
=> 40
[8] pry(main)> ObjectSpace.memsize_of(a.unshift(1))
=> 40
[9] pry(main)> ObjectSpace.memsize_of(a.unshift(1))
=> 192
[10] pry(main)> ObjectSpace.memsize_of(a.unshift(1))
=> 192
[11] pry(main)> ObjectSpace.memsize_of(a.unshift(1))
=> 192
[12] pry(main)> ObjectSpace.memsize_of(a.unshift(1))
=> 192
[13] pry(main)> ObjectSpace.memsize_of(a.unshift(1))
=> 192
[14] pry(main)> ObjectSpace.memsize_of(a.unshift(1))
=> 192
[15] pry(main)> ObjectSpace.memsize_of(a.unshift(1))
=> 192
[16] pry(main)> ObjectSpace.memsize_of(a.unshift(1))
=> 192
[17] pry(main)> ObjectSpace.memsize_of(a.unshift(1))
=> 192
[18] pry(main)> ObjectSpace.memsize_of(a.unshift(1))
=> 192
[19] pry(main)> ObjectSpace.memsize_of(a.unshift(1))
=> 192
[20] pry(main)> ObjectSpace.memsize_of(a.unshift(1))
=> 192
[21] pry(main)> ObjectSpace.memsize_of(a.unshift(1))
=> 192
[22] pry(main)> ObjectSpace.memsize_of(a.unshift(1))
=> 192
[23] pry(main)> ObjectSpace.memsize_of(a.unshift(1))
=> 192
[24] pry(main)> ObjectSpace.memsize_of(a.unshift(1))
=> 192
[25] pry(main)> ObjectSpace.memsize_of(a.unshift(1))
=> 320

```


### RArray

shared arrayの場合

- Embedded Array
- Shared Array
- Root Shared Array

```c
struct RArray {
	struct RBasic basic;
	union {
		struct {
			long len;
				union {
					long capa;
					VALUE shared;
				} aux;
			const VALUE *ptr;
		} heap;
		const VALUE ary[RARRAY_EMBED_LEN_MAX];
	} as;
};
```


`ARY_SET_SHARED_NUM`は、capaに対して値を入れる。  
Shared Arrayにおけるcapaはリフェレンスの数になる。  

```c
123 #define ARY_SET_SHARED_NUM(ary, value) do { \
124     assert(ARY_SHARED_ROOT_P(ary)); \
125     RARRAY(ary)->as.heap.aux.capa = (value); \
126 } while (0)
```

```
私の環境ではGC起動回数が約200回→約10回ほどになりました。
今回はlinux（andLinux）でも動作を確認しています。
# [ruby-dev:34355], [ruby-dev:35850] では失礼しました。両方とも直せずじまいです。

Index: array.c
===================================================================
--- array.c (revision 19779)
+++ array.c (working copy)
@@ -107,7 +107,8 @@
     } \
      } while (0)
      -#define ARY_CAPA(ary) (ARY_EMBED_P(ary) ? RARRAY_EMBED_LEN_MAX :
      RARRAY(ary)->as.heap.aux.capa)
      +#define ARY_CAPA(ary) (ARY_EMBED_P(ary) ? RARRAY_EMBED_LEN_MAX : \
      +          ARY_SHARED_ROOT_P(ary) ? RARRAY_LEN(ary) :
      +          RARRAY(ary)->as.heap.aux.capa)
      +           #define ARY_SET_CAPA(ary, n) do { \
      +                assert(!ARY_EMBED_P(ary)); \
```


```c
static VALUE
ary_ensure_room_for_unshift(VALUE ary, int argc)
{
  long len = RARRAY_LEN(ary);
  long new_len = len + argc;
  long capa;
  const VALUE *head, *sharedp;

  if (len > ARY_MAX_SIZE - argc) {
    rb_raise(rb_eIndexError, "index %ld too big", new_len);
  }

  if (ARY_SHARED_P(ary)) { // ArrayがShared Arrayである場合
    VALUE shared = ARY_SHARED(ary);
    capa = RARRAY_LEN(shared);
    if (ARY_SHARED_OCCUPIED(shared) && capa > new_len) {  // Shared Arrayが1つからだけしか参照されないかつ、unshiftをするとキャパシティを超えてしまう場合
        head = RARRAY_CONST_PTR(ary);
        sharedp = RARRAY_CONST_PTR(shared);
        goto makeroom_if_need;
    }
  }

  rb_ary_modify(ary);
  capa = ARY_CAPA(ary);
  if (capa - (capa >> 6) <= new_len) {
    ary_double_capa(ary, new_len);
  }

  /* use shared array for big "queues" */
  if (new_len > ARY_DEFAULT_SIZE * 4) {
    /* make a room for unshifted items */
    capa = ARY_CAPA(ary);
    ary_make_shared(ary);

    head = sharedp = RARRAY_CONST_PTR(ary);
    goto makeroom;
        makeroom_if_need:
    if (head - sharedp < argc) {
        long room;
      makeroom:
        room = capa - new_len;
        room -= room >> 4;
        MEMMOVE((VALUE *)sharedp + argc + room, head, VALUE, len);
        head = sharedp + argc + room;
    }
    ARY_SET_PTR(ary, head - argc);
    assert(ARY_SHARED_OCCUPIED(ARY_SHARED(ary)));
    return ARY_SHARED(ary);
  }
  else {
      /* sliding items */
    RARRAY_PTR_USE(ary, ptr, {
      MEMMOVE(ptr + argc, ptr, VALUE, len);
    });

    return ary;
  }
}

```

memcpyで常に０番目のポインタに入れている？？？なんで？

```c
  static void
  ary_memcpy0(VALUE ary, long beg, long argc, const VALUE *argv, VALUE buff_owner_ary)
  {
  #if 1
      assert(!ARY_SHARED_P(buff_owner_ary));

      if (argc > (int)(128/sizeof(VALUE)) /* is magic number (cache line size) */) {
~       rb_gc_writebarrier_remember(buff_owner_ary);
~       RARRAY_PTR_USE(ary, ptr, {
~           MEMCPY(ptr+beg, argv, VALUE, argc);
~       });
      }
      else {
~       int i;
~       RARRAY_PTR_USE(ary, ptr, {
~           for (i=0; i<argc; i++) {
~             RB_OBJ_WRITE(buff_owner_ary, &ptr[i+beg], argv[i]);
~           }
~       });
      }
  #else
```
