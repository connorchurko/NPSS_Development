function ParseEngineDeck(filename)
    disp('Parsing Engine Deck...');
    
    % Read the file, skipping the first two rows.
    % Multiple spaces are treated as a single delimiter.
    opts = delimitedTextImportOptions( ...
        'Delimiter', ' ', ...
        'ConsecutiveDelimitersRule', 'join', ...
        'LeadingDelimitersRule', 'ignore', ...
        'VariableNamingRule', 'preserve');
    
    % Row 3 contains the column names
    opts.VariableNamesLine = 3;
    
    % Data begins on row 4
    opts.DataLines = [4 Inf];
    
    % Read the data
    data = readtable(filename, opts);
    
    % Remove columns whose names start with "var"
    varColumns = startsWith(data.Properties.VariableNames, 'var', ...
                            'IgnoreCase', true);
    % Delete extra column
    data(:, varColumns) = [];
    
    % Resave data in .csv
    writetable(data, filename);
    
    disp('Engine Deck Reformatting Complete.')
end


