local names = {opener=true, output=true, codeoutput=true, notice=true, tryit=true, errordemo=true,
  hangdemo=true, program=true, challenge=true, realprog=true, datafile=true,
  teacher=true, starter=true}
function Header(el)
  if not FORMAT:match('latex') or el.level ~= 1 then return nil end
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
        local blocks = {pandoc.RawBlock('latex', '\\begin{pubcodeoutput}')}
        for _, block in ipairs(el.content) do
          if block.t == 'RawBlock' and block.format == 'latex' then
            if block.text == '\\begin{puboutput}' then
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
      local blocks = {pandoc.RawBlock('latex', '\\begin{pub' .. class .. '}')}
      local own_code_frame = class == 'output' or class == 'tryit' or
        class == 'errordemo' or class == 'hangdemo' or class == 'program' or
        class == 'starter' or class == 'datafile'
      for _, block in ipairs(el.content) do
        if not (own_code_frame and block.t == 'RawBlock' and block.format == 'latex' and
          (block.text == '\\begin{pubcode}' or block.text == '\\end{pubcode}')) then
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
    if (cp >= 0x2190 and cp <= 0x21ff) or (cp >= 0x0370 and cp <= 0x03ff) then
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
    if (cp >= 0x2190 and cp <= 0x21ff) or (cp >= 0x0370 and cp <= 0x03ff) then
      table.insert(parts, '{\\fallbackfont ' .. c .. '}')
    else
      table.insert(parts, escaped[c] or c)
    end
    if c:match('[A-Za-z0-9]') then run = run + 1 else run = 0 end
    if c:match('[_%(%)%,%.%:%/%+%-%=]') or run >= 12 then
      table.insert(parts, '\\allowbreak{}')
      run = 0
    end
  end
  return pandoc.RawInline('latex', '\\texttt{' .. table.concat(parts) .. '}')
end
