function [x, y, err, xname, yname,mname,optpars] = FRMdatdata(filespec)
% Load .dat data from FRM2 files
% Works with PANDA data in .dat format 
% V 1.1, March 2012 
% V 1.2, Sept  2015
% Simon Ward, simon.ward@psi.ch
initial
x=[]; y= []; err=[]; yname=''; xname=''; mname = '';

%----- Parse filespec --------------------------------------

[fspec, filespec] = strtok(filespec,',');
while ~isempty(filespec)
    [s, filespec] = strtok(filespec,',');
    fspec = str2mat(fspec,s);
end
[nargs,nchars] = size(fspec);

%----- Update scan parameters from filespec---------------------------

i = strmatch('X=',fspec);
if ~isempty(i)
    xname = deblank(fspec(i(end),3:nchars)); end
i = strmatch('Y=',fspec);
if ~isempty(i)
    yname = deblank(fspec(i(end),3:nchars)); end
i = strmatch('M=',fspec);
if ~isempty(i)
    mname = deblank(fspec(i(end),3:nchars)); end

filename = deblank(fspec(1,:));


% ---- Get Data from file ----------------------------------
fid = fopen(filename,'r');


if fid ==-1
    error('MATLAB:unableToFindFile','Unable to find/open file %s', filename)
end

c = onCleanup(@()fclose(fid));

i = 1;
b = true;
while(b)
    linDat = fgetl(fid);
    % Find start of data file 
    if strcmp('### Scan data',linDat)
        linDat = fgetl(fid);
        linDat = linDat(3:end);
        % Generate list of vairables
        [lspec, linspec] = strtok(linDat,char(9));
        while ~isempty(linspec)
            [s, linspec] = strtok(linspec,char(9));
            lspec = str2mat(lspec,s);
        end
        % Find the location of the needed vairables in the variable list
        xpos = [];    ypos = [];    mpos = [];
        for j = 1:length(lspec(:,1))
            if strcmp(deblank(lspec(j,:)),xname)
                xpos(length(xpos)+1) = j;
            end
            if strcmp(deblank(lspec(j,:)),yname)
                ypos(length(ypos)+1) = j;
            end
            if strcmp(deblank(lspec(j,:)),mname)
                mpos(length(mpos)+1) = j;
            end
        end
        noOfEnt = length(lspec);
        linDat = fgetl(fid);      % We do not want the units line
        j = 1;
        endOfFile = false;
        while ~endOfFile || ~feof(fid)
            linDat = fgetl(fid);
            % Are we at the end of the file?
            if strfind(linDat,'### End of NICOS data file')
                endOfFile = true;
            end
            % Parse the data line
            [lspec, linspec] = strtok(linDat,char(9));
            data(j,1) = str2double(lspec);
            for k = 2:noOfEnt
                [lspec, linspec] = strtok(linspec,char(9));
                data(j,k) = str2double(lspec);
            end
            j = j+1;
        end
        % Set return data
        x = mean(data(1:end-1,xpos),2);
        y = data(1:end-1,ypos)./data(1:end-1,mpos);
        err = sqrt(data(1:end-1,ypos))./data(1:end-1,mpos);
        clear c;
        b = false;
    end
    i = i+1;
end
