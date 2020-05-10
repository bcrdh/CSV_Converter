import glob
import datetime
import os
import pandas as pd
import re

desktopPath = os.path.expanduser("~/Desktop/")
dest = r'Output_CSVs'
filename = r'arms_modsonly_May9.csv'

col_names =  ["BCRDHSimpleObjectPID",'imageLink','filename','directory','childKey','title', 'alternativeTitle', 'creator1', 'creator2','creator3']
col_names += ['corporateCreator1','corporateCreator2','contributor1','contributor2','corporateContributor1','publisher_original','publisher_location']
col_names += ['dateCreated','description','extent','topicalSubject1','topicalSubject2','topicalSubject3','topicalSubject4','topicalSubject5']
col_names += ['geographicSubject1','coordinates','personalSubject1','personalSubject2','corporateSubject1','CorporateSubject2', 'dateIssued_start']
col_names += ['dateIssued_end','dateRange', 'frequency','genre','genreAuthority','type','internetMediaType','language1','language2','notes']
col_names += ['accessIdentifier','localIdentifier','ISBN','classification','URI']
col_names += ['source','rights','creativeCommons_URI','rightsStatement_URI','relatedItem_title','relatedItem_PID','recordCreationDate','recordOrigin']

pattern1 = r'^[A-Z][a-z]{2}-\d{2}$' #%b-%Y date (e.g. Jun-17) 
pattern2 = r'^\d{2}-\d{2}-[1-2]\d{3}$'

def splitMultiHdgs(hdgs):
    hdgs = hdgs.replace("\\,",";")
    hdgs = hdgs.split(",")
    newhdgs = []
    for hdg in hdgs:
        newhdg = hdg.replace(";", ",")
        newhdgs.append(newhdg)
    return newhdgs

def convert_date(dt_str, letter_date):
    """
    Converts an invalid formatted date into a proper date for ARCA Mods
    Correct format:  Y-m-d
    Fixes:
    Incorrect format: m-d-Y
    Incorrect format (letter date): m-d e.g. Jun-17
    :param dt_str: the date string
    :param letter_date: whether the string is a letter date. Letter date is something like Jun-17
    :return: the correctly formatted date
    """
    if letter_date:
        rev_date = datetime.datetime.strptime(dt_str, '%b-%y').strftime('%Y-%m')  # convert date to yymm string format
        rev_date_pts = rev_date.split("-")
        year_num = int(rev_date_pts[0])
        if year_num > 1999:
            year_num = year_num - 100
        year_str = str(year_num)
        rev_date_pts[0] = year_str
        revised = "-".join(rev_date_pts)

    else:
        revised = datetime.datetime.strptime(dt_str, '%d-%m-%Y').strftime(
            '%Y-%m-%d')  # convert date to YY-mm string format

    return revised

def convert():
    cModel = None
    df2  = pd.DataFrame(columns = col_names)
    df2.append(pd.Series(), ignore_index=True)
    
#     if not os.path.exists(savePath):    #if folder does not exist
#         os.makedirs(savePath) 

    df = pd.read_csv(filename,dtype = "string", encoding = 'utf_7')
    # engine = 'python', 
    #df.fillna("")
    df = df.where((pd.notna(df)), None) #convert Pandas NaNs to None 
   
    print(df)
        
    i = 1
    for item in df.itertuples():
        print("PID is " + item.PID)
        #PID
        df2.at[i, 'BCRDHSimpleObjectPID'] = item.PID
  
        #Local Identifier
        if 'mods_identifier_local_ms' in df.columns:
            localID = item.mods_identifier_local_ms
            if pd.notna(localID):
                df2.at[i,'localIdentifier'] = localID
         
        #Access Identifer
        if 'mods_identifier_access_ms' in df.columns:
            accessID = item.mods_identifier_access_ms
            if pd.notna(accessID):
                df2.at[i,'accessIdentifier'] = accessID
        #Image Link
        # Link to Image
        
        PIDparts = item.PID.split(":")
        repo = PIDparts[0] #repository code
        num = PIDparts[1] #auto-generated accession number
        imageLink = "https://bcrdh.ca/islandora/object/" + repo + "%3A" + num 
        df2.at[i, 'imageLink'] = imageLink
 
        #Title
        if 'mods_titleInfo_title_ms' in df.columns:
            title = item.mods_titleInfo_title_ms
            if pd.notna(title):
                df2.at[i,'title'] = title.replace("\,",",")
 
        #Alternative Title
        if "mods_titleInfo_alternative_title_ms" in df.columns:
            altTitle = item.mods_titleInfo_alternative_title_ms
            if pd.notna(altTitle):
                df2.at[i, 'alternativeTitle'] = altTitle.replace("\,",",")
 
        #Date
        if "mods_originInfo_dateIssued_ms" in df.columns:
            
            dt = item.mods_originInfo_dateIssued_ms
            if pd.notna(dt):
                if (re.match(pattern1, dt)): #letter date, i.e. Jun-17
                    dt = convert_date(dt, True)
                elif (re.match(pattern2, dt)): #reverse date
                    dt = convert_date(dt, False)
                df2.at[i,'dateCreated'] = dt
     
        #Date Issued Start
        if 'mods_originInfo_encoding_w3cdtf_keyDate_yes_point_start_dateIssued_ms' in df.columns:
            startDt = item.mods_originInfo_encoding_w3cdtf_keyDate_yes_point_start_dateIssued_ms
            if pd.notna(startDt):
                df2.at[i,'dateIssued_start'] = startDt

        #Date Issued End
        if 'mods_originInfo_encoding_w3cdtf_keyDate_yes_point_end_dateIssued_ms' in df.columns:
            endDt = item.mods_originInfo_encoding_w3cdtf_keyDate_yes_point_end_dateIssued_ms
            if pd.notna(endDt):
                df2.at[i,'dateIssued_end'] = startDt
     
        #Frequency (serials only)
        if 'mods_originInfo_frequency_ms' in df.columns:
            freq = item.mods_originInfo_frequency_ms
            if pd.notna(freq):
                df2.at[i,'frequency'] = freq
     
        #Extent
        if "mods_physicalDescription_extent_ms" in df.columns:
            extent = item.mods_physicalDescription_extent_ms
            if pd.notna(extent):
                df2.at[i, 'extent'] = extent
        
        #Notes
        if 'mods_note_ms' in df.columns:
            notes = item.mods_note_ms
            if pd.notna(notes):
                df2.at[i, 'notes'] = notes  
        
        #Description/Abstract
        if "mods_abstract_ms" in df.columns:
            descr = item.mods_abstract_ms
            #if type(descr) != 'pandas._libs.missing.NAType':
            if pd.notna(descr):
            #if descr is not None:
                df2.at[i, 'description'] = descr.replace("\,",",")
        
        #Personal Creators & Contributors
         
        if 'mods_name_personal_namePart_ms' in df.columns:
            roleTerm1 = ''
            roleTerm2 = ''
            names = item.mods_name_personal_namePart_ms
            if pd.notna(names):
                names = splitMultiHdgs(names)
                creatorCount = 0
                contribCount = 0

                if 'mods_name_personal_role_roleTerm_ms' in df.columns:
                    roleTerm1 = item.mods_name_personal_role_roleTerm_ms
            
                if 'mods_name_personal_role_roleTerm_text' in df.columns:
                    roleTerm2 = item.mods_name_personal_role_roleTerm_text_ms

                if pd.notna(roleTerm1):
                    roles = roleTerm1.split(",")
                else:
                    roles = roleTerm2.split(",")   
                
                while len(roles) < len(names):
                    roles.append("creator") 
                            
                for x in range(len(names)):
                
                    if roles[x] == "creator":
                        creatorCount = creatorCount + 1
                        hdg = "creator" + str(creatorCount)
                        df2.at[i,hdg] = names[x].replace("*", ",")
                 
                    else:
                        contribCount = contribCount + 1
                        hdg = "contributor" + str(contribCount)
                    
                    df2.at[i,hdg] = names[x]

        #Corporate Creators and Contributors
        if 'mods_name_corporate_namePart_ms' in df.columns:
            corpNames = item.mods_name_corporate_namePart_ms
            if pd.notna(corpNames):
                corpRoles = item.mods_name_corporate_role_roleTerm_ms.split(",")
                corpNames = corpNames.split(",")
                if len(corpNames) > 3:
                    print(item.PID + " has more than two corporate names ... please review!")
                count = 0
                for corpName in corpNames:
                    if corpRoles[count] == 'creator':
                        df2.at[i,"corporateCreator"] = corpName
                    else:
                        df2.at[i,"corporateContributor"] = corpName
 
        #topical subjects
        if 'mods_subject_topic_ms' in df.columns:
            topics = item.mods_subject_topic_ms
            if pd.notna(topics):
                topics = topics.split(",")
                for x in range(len(topics)):
                    hdg = "topicalSubject" + str(x+1)
                    df2.at[i, hdg] = topics[x]
         
        #corporate subjects
        if 'mods_subject_name_corporate_namePart_ms' in df.columns:
            corpSubs = item.mods_subject_name_corporate_namePart_ms
            if pd.notna(corpSubs):
                corpSubs = splitMultiHdgs(corpSubs)
                for x in range(len(corpSubs)):
                    hdg = "corporateSubject" + str(x+1) 
                    df2.at[i, hdg] = corpSubs[x]
         
        #personal subjects
        if 'mods_subject_name_personal_namePart_ms' in df.columns:
            pSubs = item.mods_subject_name_personal_namePart_ms
            if pd.notna(pSubs):
                pSubs = splitMultiHdgs(pSubs)
                for x in range(len(pSubs)):
                    hdg = "personalSubject" + str(x+1) 
                    df2.at[i, hdg] = pSubs[x]
        
        #temporal subject (date range)
        if 'mods_subject_temporal_ms' in df.columns:
            tempSub = item.mods_subject_temporal_ms
            if pd.notna(tempSub):
                df2.at[i,'dateRange'] = tempSub
         
        #geographic subject
        if 'mods_subject_geographic_ms' in df.columns:
            geosub = item.mods_subject_geographic_ms
            if pd.notna(geosub):
                geosubs = splitMultiHdgs(geosub)
                for x in range(len(geosubs)):
                    hdg = "geographicSubject" + str(x+1) 
                    df2.at[i, hdg] = geosubs[x]
         
        #coordinates 
        if 'mods_subject_geographic_cartographics_ms' in df.columns:
            coords = item.mods_subject_geographic_cartographics_ms
            if pd.notna(coords):
                df2.at[i,"coordinates"] = coords
                
        #classification
        if 'mods_classification_authority_lcc_ms' in df.columns:
            lcClass = item.mods_classification_authority_lcc_ms
            if pd.notna(lcClass):
                df2.at[i,'classification'] = lcClass
        
        #isbn
        if 'mods_identifier_isbn_ms' in df.columns:
            isbn = item.mods_identifier_isbn_ms
            if pd.notna(isbn):
                df2.at[i,'ISBN'] = isbn
        
        #genre
        if 'mods_genre_authority_aat_ms' in df.columns:
            genre_aat = item.mods_genre_authority_aat_ms
            if pd.notna(genre_aat):
                df2.at[i, 'genre'] = genre_aat
                df2.at[i, 'genreAuthority'] = "aat"
        elif 'mods_genre_authority_marcgt_ms' in df.columns:
            if pd.notna(item.mods_genre_authority_marcgt_ms):
                df2.at[i, 'genre'] = item.mods_genre_authority_marcgt_ms
                df2.at[i, 'genreAuthority'] = "marcgt"
        elif 'mods_originInfo_genre_ms' in df.columns:
            if pd.notna(item.mods_originInfo_genre_ms):
                df2.at[i, 'genre'] = item.mods_originInfo_genre_ms
             
        #type
        if 'mods_typeOfResource_ms' in df.columns:
            _type = item.mods_typeOfResource_ms
            if pd.notna(_type):
                df2.at[i, 'type'] = _type
         
        #internet media type
        if 'mods_physicalDescription_internetMediaType_ms' in df.columns:
            mediaType = item.mods_physicalDescription_internetMediaType_ms
            if isinstance (mediaType, str):
                df2.at[i, 'internetMediaType'] = mediaType
         
        #Languages
        if 'mods_language_languageTerm_ms' in df.columns:
            languages = item.mods_language_languageTerm_ms
            print(languages)
            print(str(type(languages)))
            if isinstance(languages, str):
                languages = languages.split(",")
                for x in range(len(languages)):
                    print("x is " + str(x))
                    print("language is " + languages[x])
                    hdg = "language" + str(x+1)
                    df2.at[i,hdg] = languages[x]
         
        #Source
        if 'mods_location_physicalLocation_ms' in df.columns:
            source = item.mods_location_physicalLocation_ms
            if pd.notna(source):
                df2.at[i, 'source'] = source
        
        #URI
        if 'mods_identifier_uri_ms' in df.columns: 
            uri = item.mods_identifier_uri_ms
            if pd.notna(uri):
                df2.at[i, 'URI'] = uri
            
        #Rights
        if 'mods_accessCondition_use_and_reproduction_ms' in df.columns:
            rights = item.mods_accessCondition_use_and_reproduction_ms
            print(rights)
            if isinstance(rights, str):
                rights = splitMultiHdgs(item.mods_accessCondition_use_and_reproduction_ms)
            
                for stmt in rights:
                    if "Permission to publish" in stmt:
                        df2.at[i, "rights"] = stmt
                    elif "rightsstatements" in stmt:
                        df2.at[i,"rightsStatement_URI"] = stmt
                    else:
                        df2.at[i,"creativeCommons_URI"] = stmt
                 
        #Related Item
        if 'mods_relatedItem_host_titleInfo_title_ms' in df.columns:
            coll_title = item.mods_relatedItem_host_titleInfo_title_ms
            coll_PID = item.mods_relatedItem_host_identifier_PID_ms
            if pd.notna(coll_title):
                df2.at[i, "relatedItem_title"] = coll_title
            if pd.notna(coll_PID):
                df2.at[i, "relatedItem_PID"] = coll_PID
         
         
        #Record Origin & Creation Date
        if 'mods_recordInfo_recordOrigin_ms' in df.columns:
            recOrigin = item.mods_recordInfo_recordOrigin_ms
            if pd.notna(recOrigin):
                df2.at[i,'recordOrigin'] = recOrigin
            recDate = item.mods_recordInfo_recordCreationDate_ms
            if pd.notna(recDate):
                recDate = recDate.split(",")
                df2.at[i, 'recordCreationDate'] = recDate[0]
 
        i = i + 1

    savePath = r'C:/Users/sharo/Desktop' + '/'
    dest = os.path.join(savePath,filename)
   
    df2.to_csv(dest, encoding='utf-8', index=False)
    
convert()