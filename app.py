import streamlit as st
from streamlit_tags import st_tags
import pandas as pd
import numpy as np

st.set_page_config( page_title="Multikriterieanalys", page_icon=":cherry_blossom:",
                layout="centered",
                initial_sidebar_state="expanded",
)

pages= st.sidebar.radio("Navigering", ('Analys', 'Guide'))


if pages == 'Analys':
    st.title("Multikriterieanalys")

    number1, number2 = st.columns((2,2))
    number1 = number1.number_input('Hur många kriterier ska analyseras?',min_value=3 ,value=5, step=1)
    number2 = number2.number_input('Hur många Alternativ ska analyseras?',min_value=1 ,value=2, step=1)

    

    keywords = st_tags(
        label='**Ange dina kriterier:**',
        text='Tryck enter för att lägga till',
        value=['Risk för skador?', 'Framkomlighet', 'Konstruktion'],
        suggestions = ["gammal crit", "gammal crit 2"],
        maxtags=number1,
        key=None)

    # st.write("### Results:")
    # st.write((keywords))

    if len(keywords) < 3:
        st.warning("Existerande bugg vid kriterier mindre än 3.. Vars snäll och addera ett till kriterie")
        st.stop()

    st.sidebar.title("Viktningsprocessen")

    vikt_tags_list = []


    if len(keywords)<3:
        vikt_tags = st.sidebar.slider(keywords[0]+' mot '+keywords[1], 1, 10, 5)
    

    else:
        def multi_over():
            for k in range(len(keywords)-1): # 0,1
                i=k+1
        

                while i < len(keywords):  # 0,1,2
                    i+=1 
                    vikt_tags = st.sidebar.slider(keywords[k]+' mot '+keywords[i-1], 1, 10, 5, key=(keywords[k]+keywords[i-1]))
                    vikt_tags_list.append(vikt_tags)

                vikt_tags_list.append("next")

                
            vikt_tag_list_size = len(vikt_tags_list)
            idx_list = [idx + 1 for idx, val in enumerate(vikt_tags_list) if val == "next"]

            
            res = [vikt_tags_list[i: j] for i, j in
                    zip([0] + idx_list, idx_list + ([vikt_tag_list_size] if idx_list[-1] != vikt_tag_list_size else []))]

            for x in res:
                x.remove("next")
                
            return res


        vikt_tags = multi_over()



    def calc_prio():
        # creating 2d with 0 padding arrays
        length_keywords= len(keywords)
        # first_a = np.zeros((length_keywords,length_keywords))

        first_fake_matrix=np.array([np.array(xi) for xi in vikt_tags],dtype=object)

        length = max(map(len, vikt_tags))

        arr_placeholder = np.array([])

        for pad in range(length):
            new_vikt = (np.pad(first_fake_matrix[pad],[pad+1,0], mode="constant"))
            arr_placeholder = np.append(arr_placeholder,new_vikt,axis=0)

        fake_matrix = arr_placeholder.reshape((length, length_keywords))


        ## creating array
        zero_matrix_holder = np.zeros((length_keywords,length_keywords))

        np.fill_diagonal(zero_matrix_holder, 1)

        for index, x in np.ndenumerate(zero_matrix_holder):
            if index[1] > index[0]:
                zero_matrix_holder[index] = fake_matrix[index]

            elif index[1] < index[0]:
                zero_matrix_holder[index] = 10-(fake_matrix[index[1],index[0]])

        df = pd.DataFrame(zero_matrix_holder)

        df2= np.power(df.prod(axis = 1),(1/length_keywords))
        df3 = df2/df2.sum(axis=0)
        df4 = df3.to_frame()
        df4 = df4.T
        df4.columns= keywords
        return df4 ,df3, length, length_keywords

    prio_weights,prio_holder, length, length_keywords = calc_prio()

    st.write("**Resultat från viktningen**")

    st.write(prio_weights)


    my_expander = st.expander(label='Utvärdera dina alternativ: ')
    with my_expander:

        alt_tags_list = []

        def multi_text():
            
            for alt in range(number2):
                st.write("Alternativ "+ str(alt+1) + " :")
                for crit in range(len(keywords)):

                    text_tag = st.text_input("Parameter "+ str(crit+1)+ " :" , value="0" , key=str(crit)+str(alt))
                    alt_tags_list.append(float(text_tag))

                alt_tags_list.append("next")

                
            alt_tag_list_size = len(alt_tags_list)
            idx_list = [idx + 1 for idx, val in enumerate(alt_tags_list) if val == "next"]

            
            res = [alt_tags_list[i: j] for i, j in
                    zip([0] + idx_list, idx_list + ([alt_tag_list_size] if idx_list[-1] != alt_tag_list_size else []))]

            for x in res:
                x.remove("next")
                
            return res

        texts_inputs= multi_text()

    if np.sum(texts_inputs[0]) <=0:
        st.warning("Gå in i expandern ovanför och fyll i dina alternativ")
        st.stop()

    listers = []

    for items in range(length_keywords):
        lst2 = [item[items] for item in texts_inputs]
        listers.append(np.sum(lst2))

## Adding labels to rows
    Alternativ_list= []

    for i in range(len(texts_inputs)):
        add_alt_list = "Alternativ "+ str(i)
        Alternativ_list.append(add_alt_list)

    arr_list = np.array(listers)
    arr_texts = np.array(texts_inputs)
    arring_texts = (arr_texts/arr_list)

#    st.write("normalized alt",arring_texts)

    prio_vector = np.array(prio_holder)
    text_prio = np.array(arring_texts)

    # to_priotize_norm= np.dot(np.reshape(normalized_arr,(number2, length_keywords)),prio_vector)

    multi_priotize =text_prio*prio_vector

    df_alternatives = pd.DataFrame(multi_priotize)
    df_alternatives.columns= keywords
    df_alternatives.index = Alternativ_list

    to_priotize= np.dot(text_prio,prio_vector)



    if number2 > 1:
        st.write("**Aggregerad resultat från Alternativ x Vikterna**")
        image =st.bar_chart(df_alternatives)

        st.download_button("Skicka dina resultat till databasen", "Nu har resultatet 'skickats till databasen'", "Resultat_skickat.text")

else:
    st.title("Hur det funkar!")

    video_file = open('myvideos.webm', 'rb')
    video_bytes = video_file.read()
    st.video(video_bytes)

    st.write('''Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt
     ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut 
     aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. 
     Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.''')


