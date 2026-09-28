local names = {opener=true, output=true, codeoutput=true, notice=true, tryit=true, errordemo=true,
  hangdemo=true, program=true, challenge=true, realprog=true, datafile=true,
  teacher=true, starter=true, goals=true, recap=true}
function Header(el)
  if not FORMAT:match('latex') then return nil end
  -- Quarto gives the heading-less the-index.qmd an empty chapter: a blank page before
  -- \printindex, which opens its own chapter.
  if el.level == 1 and #el.content == 0 then return {} end
  if (el.level == 3 or el.level == 4) and el.content[1] then
    local title = pandoc.utils.stringify(el.content)
    if title:match('^Exercise %d+') or title:match('^Question %d+') or
       title:match('^Problem %d+') or title:match('^Challenge — ') then
      return {pandoc.RawBlock('latex', '\\Needspace{16\\baselineskip}'), el}
    end
  end
  if el.level ~= 1 then return nil end
  local label = el.attributes['pub-label']
  if label == nil then return nil end
  local prefix = ''
  if el.attributes['pub-mainmatter'] == 'true' then prefix = '\\mainmatter\n' end
  prefix = prefix .. '\\pubchapterlabel{' .. label .. '}'
  el.attributes['pub-label'] = nil
  el.attributes['pub-mainmatter'] = nil
  return {pandoc.RawBlock('latex', prefix), el}
end
function Div(el)
  for _, class in ipairs(el.classes) do
    if names[class] then
      if class == 'codeoutput' then
        local blocks = {pandoc.RawBlock('latex', '\\Needspace{9\\baselineskip}\n\\begin{pubcodeoutput}')}
        for _, block in ipairs(el.content) do
          if block.t == 'RawBlock' and block.format == 'latex' then
            if block.text:match('\\begin{puboutput}$') then
              table.insert(blocks, pandoc.RawBlock('latex',
                '\\tcblower\\textbf{\\scriptsize\\color{SteelBlue}Output}\\par\\vspace{-0.5\\baselineskip}'))
            elseif block.text ~= '\\end{puboutput}' and block.text ~= '\\begin{pubcode}' and
                block.text ~= '\\end{pubcode}' then
              table.insert(blocks, block)
            end
          else
            table.insert(blocks, block)
          end
        end
        table.insert(blocks, pandoc.RawBlock('latex', '\\end{pubcodeoutput}'))
        return blocks
      end
      local opening = class == 'challenge' and '\\begin{pubchallenge}' or
        '\\Needspace{9\\baselineskip}\n\\begin{pub' .. class .. '}'
      local blocks = {pandoc.RawBlock('latex', opening)}
      local own_code_frame = class == 'output' or class == 'tryit' or
        class == 'errordemo' or class == 'hangdemo' or class == 'program' or
        class == 'starter' or class == 'datafile'
      for _, block in ipairs(el.content) do
        if own_code_frame and block.t == 'RawBlock' and block.format == 'latex' and
          block.text:match('^\\begin{pubcode}') then
          if block.text:match('\\footnotesize') then
            table.insert(blocks, pandoc.RawBlock('latex', '\\footnotesize'))
          end
        elseif not (own_code_frame and block.t == 'RawBlock' and block.format == 'latex' and
          block.text == '\\end{pubcode}') then
          table.insert(blocks, block)
        end
      end
      table.insert(blocks, pandoc.RawBlock('latex', '\\end{pub' .. class .. '}'))
      return blocks
    end
  end
end
function CodeBlock(el)
  if not FORMAT:match('latex') then return nil end
  for _, class in ipairs(el.classes) do
    if class == 'answer-code' then
      return {pandoc.RawBlock('latex', '\\begin{pubcode}\\footnotesize'), el,
              pandoc.RawBlock('latex', '\\end{pubcode}')}
    end
  end
  return {pandoc.RawBlock('latex', '\\begin{pubcode}'), el,
          pandoc.RawBlock('latex', '\\end{pubcode}')}
end
function Str(el)
  if not FORMAT:match('latex') then return nil end
  local changed = false
  local out = {}
  local escaped = {
    ['\\'] = '\\textbackslash{}', ['{'] = '\\{', ['}'] = '\\}',
    ['$'] = '\\$', ['%'] = '\\%', ['&'] = '\\&', ['#'] = '\\#',
    ['_'] = '\\_', ['^'] = '\\textasciicircum{}', ['~'] = '\\textasciitilde{}',
  }
  for _, cp in utf8.codes(el.text) do
    local char = utf8.char(cp)
    if (cp >= 0x2190 and cp <= 0x21ff) or (cp >= 0x0370 and cp <= 0x03ff) or
       cp == 0x25b8 or cp == 0x2610 then
      changed = true
      table.insert(out, '{\\fallbackfont ' .. char .. '}')
    else
      table.insert(out, escaped[char] or char)
    end
  end
  if changed then return pandoc.RawInline('latex', table.concat(out)) end
  return nil
end
function Code(el)
  if not FORMAT:match('latex') then return nil end
  local escaped = {
    ['\\'] = '\\textbackslash{}', ['{'] = '\\{', ['}'] = '\\}',
    ['$'] = '\\$', ['%'] = '\\%', ['&'] = '\\&', ['#'] = '\\#',
    ['_'] = '\\_', ['^'] = '\\textasciicircum{}', ['~'] = '\\textasciitilde{}',
  }
  local parts = {}
  local run = 0
  for _, cp in utf8.codes(el.text) do
    local c = utf8.char(cp)
    if (cp >= 0x2190 and cp <= 0x21ff) or (cp >= 0x0370 and cp <= 0x03ff) or
       cp == 0x25b8 or cp == 0x2610 then
      table.insert(parts, '{\\fallbackfont ' .. c .. '}')
    else
      table.insert(parts, escaped[c] or c)
    end
    if c:match('[A-Za-z0-9]') then run = run + 1 else run = 0 end
    if c == '\\' or c:match('[_%(%)%,%.%:%/%+%-%=]') or run >= 12 then
      table.insert(parts, '\\allowbreak{}')
      run = 0
    end
  end
  return pandoc.RawInline('latex', '\\texttt{' .. table.concat(parts) .. '}')
end
-- A chapter's last box, when short, is marked with \pubfinalbox{lines} (theme.tex) so that it does not
-- sit alone on an otherwise empty page. This pass runs before the others, on the original blocks.
local function box_lines(block)
  if block.t == 'CodeBlock' then
    local _, breaks = block.text:gsub('\n', '')
    return breaks + 1
  end
  if block.t ~= 'Div' then return nil end
  local panel = false
  for _, class in ipairs(block.classes) do
    if names[class] and class ~= 'challenge' then panel = true end
  end
  if not panel then return nil end
  local lines = 1
  for _, inner in ipairs(block.content) do
    if inner.t == 'CodeBlock' then
      local _, breaks = inner.text:gsub('\n', '')
      lines = lines + breaks + 1
    else
      lines = lines + math.ceil(#pandoc.utils.stringify(inner) / 80)
    end
  end
  return lines
end
local function chapter_end(blocks, index)
  for next_index = index + 1, #blocks do
    local block = blocks[next_index]
    if block.t == 'Header' then return block.level == 1 end
    -- Quarto separates book files with raw metadata markers, as a RawBlock or a raw-only Para.
    local marker = block.t == 'RawBlock'
    if block.t == 'Para' and #block.content > 0 then
      marker = true
      for _, inline in ipairs(block.content) do
        if inline.t ~= 'RawInline' then marker = false end
      end
    end
    if not marker then return false end
  end
  return true
end
local function mark_final_boxes(doc)
  if not FORMAT:match('latex') then return nil end
  local blocks = {}
  for index, block in ipairs(doc.blocks) do
    local lines = box_lines(block)
    if lines and lines <= 3 and chapter_end(doc.blocks, index) then
      table.insert(blocks, pandoc.RawBlock('latex', '\\pubfinalbox{' .. lines .. '}'))
    end
    table.insert(blocks, block)
  end
  doc.blocks = blocks
  return doc
end
return {{Pandoc = mark_final_boxes},
        {Header = Header, Div = Div, CodeBlock = CodeBlock, Str = Str, Code = Code}}
