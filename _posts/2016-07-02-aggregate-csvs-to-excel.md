---
layout: post
title: 複数のCSVファイルをエクセルにまとめる
date: '2016-07-01T23:19:00.000+09:00'
author: s sato
tags:
- ruby
---

複数のCSVを一つのエクセルにまとめたい場合には、[axlsx](https://github.com/randym/axlsx)がとても便利。  
テーブルのスタイルも変更できる。

```ruby
require 'csv'
require 'axlsx'

csvfiles = %w(test1.csv test2.csv)

Axlsx::Package.new do |p|

  def right_bottom_ref(cols,rows)
	row_ref = rows.to_s
	col_ref = 'A'
	(cols-1).times{col_ref.next!}
	return "A1:#{col_ref}#{row_ref}"
  end

  csvfiles.each do |csv|
    p.workbook.add_worksheet(:name => csv) do |sheet|
	  CSV.foreach(csv) do  |row|
	    sheet.add_row row
	end
	ref = right_bottom_ref sheet.cols.length, sheet.rows.length
	sheet.add_table(ref, :name => csv, :style_info => { :name => "TableStyleMedium21" })
    end
  end
  p.serialize('sample.xlsx')
end
```
