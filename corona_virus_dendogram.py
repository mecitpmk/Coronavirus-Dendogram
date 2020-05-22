

import clusters
from tkinter import filedialog
import os
import pandas as pd
from PIL import ImageTk
from tkinter import *
from PIL import Image,ImageDraw


class Data:    
    def load_ct_data(self,data_name=None):
        """
        Notes:
            data_name (str) - Comes from tkinter.askfileopen 
            if the given parameeter match with the excell files this function will be work.
            In this function python willl collect information from the Columns
            Which are ;
                Total cases , Total Deaths , Total Recovered , Active cases , Serious Cases , 
                                        Total Case/1M Population
            after that python will !create object! for the corresponding country.
        """                
        if data_name:
            self.ct_data=pd.read_excel(data_name)
            self.ct_data.fillna(0,inplace=True)
            for a in range(len(self.ct_data)):
                c_name=self.ct_data.loc[a,"Country"]
                if c_name == "Total:":
                    break
                total_cases=self.ct_data.loc[a,"Total Cases"]
                total_deaths=self.ct_data.loc[a,"Total Deaths"]
                total_recovered=self.ct_data.loc[a,"Total Recovered"]
                active_cases=self.ct_data.loc[a,"Active Cases"]
                serious_cases=self.ct_data.loc[a,"Serious Cases"]
                total_case_pop=self.ct_data.loc[a,"Total Case/1M Population"]
                Country(c_name,total_cases,total_deaths,total_recovered,active_cases,serious_cases,total_case_pop)

    def load_test_statistics(self,data_name=None):
        """
        Notes:
            data_name (str) - Comes from tkinter.askfileopen 
            if the given parameeter match with the excell files this function will be work.
            In this function python will collect other information from statisctis data.
            Python will match the other information if the corresponding country names in the excell files
            For example Luxembourg not in the statistics dataset. and in the dataset there some information like Positive Results.
            Python automatically find the luxembourg object dictionary and fill the information with 0 !
        """
        if data_name:
            self.stat_data=pd.read_excel(data_name)
            self.stat_data.fillna(0,inplace=True)
            for a in range(len(self.stat_data)):
                ct_name=self.stat_data.loc[a,"Country or region"]
                ct_name=ct_name.split()
                ct_name=ct_name[0]
                total_tests=self.stat_data.loc[a,"Total Tests"]
                positive_results=self.stat_data.loc[a,"Positive Results"]
                tests_pop=self.stat_data.loc[a,"Tests/1M Pop."]
                positives_pop=self.stat_data.loc[a,"Positive Results/1K Pop."]
                for ct_obj in Country.all_countries:
                    if ct_obj.country == ct_name:
                        ct_obj.total_test=total_tests
                        ct_obj.positive_result=positive_results
                        ct_obj.test_pop=tests_pop
                        ct_obj.positive_pop=positives_pop
            for ct in Country.all_countries:ct.make_feeds()
            self.update_feeds()
    def update_feeds(self):
        """
        Notes:
            If the Country don't have information about statistics it will fill with 0!
            Example : {Luxembourg:{Total Tests:0}}
        """        
        new_dict={}
        for key,value in Country.feeds.items():
            for other_value in value:
                for test in Country.cases:
                    if other_value == test:
                        new_dict.setdefault(key,{})
                        new_dict[key][other_value]=value[other_value]
                    else:
                        new_dict[key].setdefault(test,0)
        Country.feeds=new_dict
        self.change_names()
    def change_names(self):
        """
        Notes:
            Change Names to New names:
            if we dont do that. It will show like that in the jpg:
                total_case
            But if this function work it will show like that in jpg:
                Total Cases
        """    
        self.change_dict=dict(total_case="Total Cases",total_death="Total Death",total_recovered="Total Recovered",
                            active_case="Active Cases",serious_case="Serious Cases",total_case_population="Total Cas. Population",
                                total_test="Total Tests",positive_result="Positive Results",test_pop="Test Population",positive_pop="Positive Res. Population")
        new_d={}
        for a in self.change_dict:
            for country,country_dict in Country.feeds.items():
                for b in country_dict:
                    if a == b:
                        new_d.setdefault(country,{})
                        new_d[country][self.change_dict[a]]=country_dict[b]
        Country.feeds=new_d

class SortMyList:
    """
        sorted_by_name=Ct_list.sort_list(name=True)
        sorted_by_cases=Ct_list.sort_list(name=False)
    """
    def sort_list(self,name=False):
        """
        
        Keyword Arguments:
            name {bool} - If the true python will return sorted by name else:
                                Python will return sorted by Number!
        
        Returns:
            [list] - if the kwargs True return corresponding tuples:
        """        
        reverse=True
        if not name:
            idx=1
        elif name:
            idx=0
            reverse=False
        list=Country.obj_and_cases.copy()
        list.sort(key= lambda s : s[idx],reverse=reverse)
        return list
 
class Country:
    all_countries=[]
    obj_and_cases=[]
    feeds={}
    cases={}
    def __init__(self,country,total_case,total_death,total_recovered,
                        active_case,serious_case,total_case_population):
        self.country=country
        self.total_case=total_case
        self.total_death=total_death
        self.total_recovered=total_recovered
        self.active_case=active_case
        self.serious_case=serious_case
        self.total_case_population=total_case_population
        Country.all_countries.append(self)
        Country.obj_and_cases.append((self.country,self.total_case))
    def make_feeds(self):
        """
        Notes:
            In this function we are accessing object dictionary.
            In this function we transferring Country.feeds to all information  from Object.
            Also we are transferring all the cases to Country.cases 
        """        
        ct=""
        for key,value in self.__dict__.items():
            if key == "country":
                ct=value
                Country.feeds[ct]={}
            else:
                Country.feeds[ct][key]=value
                Country.cases.setdefault(key,1)
    def __repr__(self):
        return (f'{self.country} ({self.total_case})')
    
class GUI(Frame):
    def __init__(self,inheritance):
        """
        Objects:
            Data() - > reading excell files.
            SortMyList() -> sorting given lists.
            Country -> when read the excell files create object for corresponding Country.
        """        
        self.inheritance=inheritance
        Frame.__init__(self,inheritance)
        self.grid()
        self.initGUI()
        self.data=Data()
        self.ct_l=SortMyList()
        self.returned_selected={}
        self.returned_crit={}
    def initGUI(self):
        self.BIG_TEXT=Label(self,text="CORONAVIRUS DATA ANALYSIS TOOL",bg="red",fg="white",font=("Helvetica",14,"bold"),anchor=CENTER)
        self.BIG_TEXT.grid(row=0,column=0,sticky=E+W+S+N,columnspan=6)

        self.canvasFrame=Frame(self,borderwidth=3,relief=GROOVE)
        self.canvasFrame.grid(row=1,column=0,padx=10,pady=10,columnspan=6)
        
        self.canvas=Canvas(self.canvasFrame)
        self.canvas.pack(ipadx=300,ipady=100)
        self.canVeritcalScr=Scrollbar(self.canvas,orient="vertical",command=self.canvas.yview)
        self.canVHorizontalScr=Scrollbar(self.canvas,orient="horizontal",command=self.canvas.xview)
        self.canVHorizontalScr.pack(side="bottom",fill="x")
        self.canVeritcalScr.pack(side="right",fill="y")
        self.canvas.configure(xscrollcommand=self.canVHorizontalScr.set,yscrollcommand=self.canVeritcalScr.set)
        

        self.dataButton=Button(self,text="Upload Country Data",anchor=E,command=self.ctData)
        self.dataButton.grid(row=2,column=2,padx=10,pady=10,sticky=E)
        
        self.statsButton=Button(self,text="Upload Test Statistics",anchor=E,command=self.statData)
        self.statsButton.grid(row=2,column=3,padx=10,pady=10,sticky=E)

        self.sortFrame=Frame(self,borderwidth=3,relief=GROOVE)
        self.sortFrame.grid(row=3,column=0,padx=10,pady=10)

        self.sortLabel=Label(self.sortFrame,text="Sort Countries")
        self.sortLabel.grid(row=0,column=0,padx=5,pady=5)
        self.sortbyNameBut=Button(self.sortFrame,text="Sort By Name",command=self.sortbyName)
        self.sortbyNameBut.grid(row=1,column=0,padx=5,pady=5)

        self.sortbyCaseBut=Button(self.sortFrame,text="Sort by Total Cases",command=self.sortbyCase)
        self.sortbyCaseBut.grid(row=2,column=0,padx=5,pady=5)

        self.ctriesLabel=Label(self,text="Countries:")
        self.ctriesLabel.grid(row=3,column=1,padx=10,pady=10,sticky=E)

        self.ctriesListbox=Listbox(self,selectmode="multiple",width=45,exportselection=0)
        self.ctriesListbox.grid(row=3,column=2,padx=10,pady=10)
        self.ctriesListbox.propagate(False)
        self.ctriesListbox.bind("<<ListboxSelect>>",self.ctriesSelected)
        
        self.scrool=Scrollbar(self)
        self.scrool.grid(row=3,column=2,sticky=E,ipady=55,padx=10)
        self.ctriesListbox.configure(yscrollcommand=self.scrool.set)
        self.scrool.config(command=self.ctriesListbox.yview)


        self.critLabel=Label(self,text="Criterias:")
        self.critLabel.grid(row=3,column=3,padx=10,pady=10,sticky=E)

        self.critListbox=Listbox(self,selectmode="multiple",width=45,exportselection=0)
        self.critListbox.grid(row=3,column=4,padx=10,pady=10)
        self.critListbox.propagate(False)
        self.critListbox.bind("<<ListboxSelect>>",self.critSelected)

        self.scrool2=Scrollbar(self)
        self.scrool2.grid(row=3,column=4,sticky=E,ipady=55,padx=10)
        self.critListbox.configure(yscrollcommand=self.scrool2.set)
        self.scrool2.config(command=self.critListbox.yview)
    
        self.AnalyseFrame=Frame(self,borderwidth=3,relief=GROOVE)
        self.AnalyseFrame.grid(row=3,column=5,padx=10,pady=10)

        self.AnalyseLabel=Label(self.AnalyseFrame,text="Analyse Data:")
        self.AnalyseLabel.grid(row=0,column=0,padx=5,pady=5)

        self.AnalyseCountryBut=Button(self.AnalyseFrame,text="Cluster Countries",command=lambda : self.write_files("Country"))
        self.AnalyseCountryBut.grid(row=1,column=0,padx=5,pady=5)

        self.AnalyseCriteriaBut=Button(self.AnalyseFrame,text="Cluster Criterias",command=lambda : self.write_files("Criterias"))
        self.AnalyseCriteriaBut.grid(row=2,column=0,padx=5,pady=5)

    def sortbyName(self):
        """
        Notes:
            thanks to SortMyLis() object we can sort Listbox.
            Be careful function parameeter is True! it means that sort by Name.
        """        
        sorted_by_N=self.ct_l.sort_list(name=True)
        self.ctriesListbox.delete(0,END)
        for ct,case in sorted_by_N:
            string=(f'{ct} - {case}')
            self.ctriesListbox.insert(END,string)
    def sortbyCase(self):
        """
        Notes:
            thanks to SortMyLis() object we can sort Listbox.
            Be careful function parameeter is True! it means that sort by CASES!.
        """
                        
        sorted_by_C=self.ct_l.sort_list(name=False)
        self.ctriesListbox.delete(0,END)
        for ct,case in sorted_by_C:
            string=(f'{ct} - {case}')
            self.ctriesListbox.insert(END,string)
    def catchLocation(self):
        """
        Returns:
            [str] -- return XLSX location Completely Ex-> C:/Users/Mecit/Desktop/mp3/dataset.xlsx
        """        
        get_current_directory=str(os.getcwd())
        get_file=str(filedialog.askopenfilename(initialdir=get_current_directory,filetypes=(("xlsx files","*.xlsx"),("all files","*.*"))))
        return get_file
    def ctData(self):
        """
        Notes:
            Collect datas from coronavirus_country_data.xlsx
            and append to listbox all the information.
        """        
        ct_excell=self.catchLocation()
        self.data.load_ct_data(ct_excell)
        for ct,cases in Country.obj_and_cases:
            string=(f'{ct} - {cases}')
            self.ctriesListbox.insert(END,string)
    def statData(self):
        """
        Notes:
            Collect all data from   test_statistics.xlsx
            and append  criteria Listbox.
        """        
        stat_excell=self.catchLocation()
        self.data.load_test_statistics(stat_excell)
        for values in self.data.change_dict.values():
            self.critListbox.insert(END,values)
    def ctriesSelected(self,event):
        """
        Notes:
            Python will identify which country selected. Appendind selected country to list.
        """        
        self.capture_event=event.widget
        self.x=self.capture_event.curselection()
        self.selected_ctr=[self.ctriesListbox.get(a) for a in self.x]
        self.clear_selected=[]
        for ct_case in self.selected_ctr:
            splitted=ct_case.split()
            ct_name=splitted[0]
            self.clear_selected.append(ct_name)
        self.returned_selected=self.only_selected_conutry()
    def only_selected_conutry(self):
        """
        Notes:
            This function remove country except selected country.
        Returns:
            {dict} -  ex . {Turkey:{positive  result : 1 }}
        """
        new_dict={}
        for a in self.clear_selected:
            for b in Country.feeds:
                if a == b:
                    new_dict[a]=Country.feeds[b]
        return new_dict
    
    def critSelected(self,event):
        """
        Notes:
            Python will update selected criteria.Because if the user
            wants to Cluster data this function carries important role.
        """    
        capture_event=event.widget
        self.y=capture_event.curselection()
        self.selected_criteria=[self.critListbox.get(a) for a in self.y]
        self.returned_crit=self.only_selected_criteria()
        print(self.returned_crit)
    def only_selected_criteria(self):
        """
        Notes:
            This function only returnes country and selected criterias.
                Ex: {Turkey:{Total Cases : 5 , Positive Results : 0}} etc..
        Returns:
            {dict} -- dictionary of selected criteria and corresponding country
        """        
        if len(self.returned_selected) == 0:
            self.returned_selected=Country.feeds
        if not hasattr(self,"selected_criteria"):
            self.selected_criteria=[]
            for a in Country.cases.values():self.selected_criteria.append(a)
        new_dict={}
        for a in self.selected_criteria:
            for ct in self.returned_selected:
                for acces in self.returned_selected[ct]:
                    if a == acces:
                        new_dict.setdefault(ct,{})
                        new_dict[ct][acces]=self.returned_selected[ct][acces]
        return new_dict
    def write_files(self,param):
        """
        Notes:
            Parameeter will be specified in button commands:
            Python will understand wich button pressed or not easily.
            Moreover, python will write a txt file for the clusturing.
        """
        # print(f'returned select = {self.returned_selected}  - returned crit , {self.returned_crit}')
        if len(self.returned_selected) == 0 and len(self.returned_crit) == 0:
            given_dict=Country.feeds
        else:
            if len(self.returned_crit) == 0:
                given_dict=self.returned_selected
            elif len(self.returned_selected) == 0:
                self.returned_selected=Country.feeds
                given_dict=self.returned_crit
            else:
                given_dict=self.only_selected_criteria()
    
        self.writed_names="clustured.txt"
        with open(self.writed_names,"w") as text_file:
            text_file.write("Countries")
            for cnt,cnt_dict in given_dict.items():
                for keys in cnt_dict:
                    text_file.write(f'\t{keys}')
                break
            text_file.write('\n')
            for ct,values_dict in given_dict.items():
                text_file.write(ct)
                for get_key,get_value in values_dict.items():
                    text_file.write(f'\t{get_value}')
                text_file.write("\n")
        if param == "Country":
            self.get_clusture("Country")
        elif param == "Criterias":
            self.get_clusture("Criterias")
    def get_clusture(self,param):
        """
        param - str -> Parameeter will be specified in self.writefiles
        if param is Country it will show Country clusters
        if param is Criterias it will show data clusters
        """        
        country_names,records,records_data=clusters.readfile(self.writed_names)
        if param == "Country":
            clust=clusters.hcluster(records_data)
            label=country_names
        elif param == "Criterias":
            rotated=clusters.rotatematrix(records_data)
            clust=clusters.hcluster(rotated)
            label=records
        self.jpg_names='clustured2.jpg'
        clusters.drawdendrogram(clust,labels=label,jpeg=self.jpg_names)
        self.show_image()
    def show_image(self):
        """
        Notes:
            Python will upload jpg files to canvas.
        """        
        im = Image.open(self.jpg_names)
        self.canvas.image = ImageTk.PhotoImage(im)
        self.canvas.create_image(0,0, anchor=NW ,image=self.canvas.image)
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))



if __name__ == "__main__":        
    root=Tk()
    runSystem=GUI(root)
    root.title("Coronavirus Estimator")
    root.mainloop()
