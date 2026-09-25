local names = {opener=true, output=true, notice=true, tryit=true, errordemo=true,
  hangdemo=true, program=true, challenge=true, realprog=true, datafile=true,
  teacher=true, starter=true}
function Div(el)
  for _, class in ipairs(el.classes) do
    if names[class] then
      local blocks = {pandoc.RawBlock('latex', '\\begin{pub' .. class .. '}')}
      for _, block in ipairs(el.content) do table.insert(blocks, block) end
      table.insert(blocks, pandoc.RawBlock('latex', '\\end{pub' .. class .. '}'))
      return blocks
    end
  end
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
