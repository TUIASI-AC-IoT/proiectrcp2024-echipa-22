#                                                               Implementare mDNS și DNS-SD. Documentație Tehnică 

Introducere:
Acest proiect implementează un sistem de descoperire a serviciilor folosind mDNS (Multicast DNS) și DNS-SD (DNS Service Discovery). Aplicația permite monitorizarea resurselor sistemului și expunerea lor ca servicii în rețeaua locală.

# Introducere:

1. **mDNS (Multicast DNS)**  este o tehnologie care permite realizarea operațiilor de tip DNS într-o rețea locală mică, fără a necesita un server DNS centralizat. Fiecare dispozitiv din rețea poate obține automat un nume unic de tipul „MyComputer.local”, făcând mai ușoară identificarea și comunicarea între dispozitivele conectate.


# Tipuri de mesaje mDNS
1. Query (Cerere):
Acest mesaj este trimis atunci când un dispozitiv dorește să afle informații despre un alt dispozitiv din rețea. De exemplu, dacă un dispozitiv vrea să cunoască adresa IP asociată unui anumit nume (ex. „MyComputer.local”), va trimite un mesaj de tip query. Query-urile sunt trimise către o adresă de multicast specială (de obicei, 224.0.0.251 pentru IPv4 sau FF02::FB pentru IPv6, 5353 port standard), astfel încât toate dispozitivele din rețea să le poată recepționa.
2. Response (Răspuns):
Atunci când un dispozitiv primește o cerere care îi corespunde, acesta trimite un răspuns mDNS. De exemplu, dacă un dispozitiv a primit o cerere pentru „MyComputer.local” și acesta este numele său, va răspunde cu adresa sa IP. Răspunsurile mDNS includ diferite tipuri de înregistrări DNS, cum ar fi A (pentru adresa IP), PTR (pentru servicii), SRV (pentru informații despre serviciu, port și protocol) și TXT (pentru date suplimentare despre serviciu). \
![Imagine1](https://github.com/TUIASI-AC-IoT/proiectrcp2024-echipa-22/blob/main/diverse/mDNS.png)

# DNS-SD (DNS-based Service Discovery)
2. **DNS-SD (DNS-based Service Discovery)** este o metodă prin care dispozitivele dintr-o rețea locală pot fi descoperite și identificate în funcție de serviciile pe care le oferă. Acest lucru permite dispozitivelor să colaboreze fără configurări complexe; de exemplu, un telefon poate trimite comanda de imprimare către o imprimantă din aceeași rețea, datorită faptului că ambele dispozitive se pot recunoaște reciproc și pot comunica direct. 

# Tipuri de înregistrări DNS folosite în DNS-SD
1. PTR (Pointer Record):
Aceste înregistrări indică prezența unui serviciu și direcționează către o înregistrare specifică de tip SRV. De exemplu, un serviciu de tip „_http._tcp.local” va avea un registru PTR care indică toate dispozitivele din rețea care rulează un server HTTP.
2. SRV (Service Record):
Înregistrările SRV oferă informații despre locația unui serviciu, inclusiv numele dispozitivului, portul pe care funcționează serviciul și protocolul (TCP sau UDP). Aceasta ajută dispozitivele să știe exact cum să acceseze serviciul respectiv.
3. TXT (Text Record):
Înregistrările TXT furnizează detalii suplimentare despre serviciu, cum ar fi versiunea software, funcționalități disponibile sau alte informații care pot fi utile pentru clienți. Acestea sunt transmise sub formă de perechi cheie-valoare.
4. A (Address Record):
Înregistrările A sunt folosite pentru a oferi adresa IP a unui dispozitiv, permițând accesul direct la serviciul găzduit pe dispozitivul respectiv. \
![Imagine2](https://github.com/TUIASI-AC-IoT/proiectrcp2024-echipa-22/blob/main/diverse/dns-ds.png)


# Cerințe Funcționale:

1.Utilizarea modulului socket pentru comunicație \
2.Implementarea structurii pachetelor mDNS/DNS-SD \
3.Monitorizarea resurselor sistemului (procesor, memorie, temperatură) \
4.Descoperirea serviciilor în rețeaua locală \
5.Implementarea mecanismului de caching \
6.Control TTL pentru monitorizare


Pașii de implementare:
# 1. Utilizarea modulului socket pentru comunicație
Primul pas în implementarea mDNS și DNS-SD este configurarea unui socket UDP care va trimite și va primi mesaje prin rețea folosind adrese multicast. Modulul socket din Python este ideal pentru acest tip de comunicație, fiind capabil să interacționeze cu rețelele de multicast.

Pașii de implementare:

Crearea unui socket UDP care va comunica pe portul standard pentru mDNS (5353). \
Configurarea socket-ului pentru a permite trimiterea și primirea pachetelor prin multicast, pe adresa 224.0.0.251. \
Trimiterea pachetelor DNS folosind socket-ul configurat, respectând structura specifică mDNS/DNS-SD. \
Ascultarea pe socket pentru a primi răspunsuri de la alte dispozitive din rețea, care vor include informațiile solicitate. 

# 2. Implementarea structurii pachetelor mDNS/DNS-SD
Pachetele DNS care sunt utilizate în mDNS și DNS-SD trebuie să respecte formatul specificat de RFC-urile 6762 și 6763. Aceste pachete pot include mai multe tipuri de înregistrări, cum ar fi SRV, PTR, A și TXT.

Pașii de implementare:

Fiecare pachet DNS va conține tipul înregistrării (A, PTR, SRV, TXT), precum și numele și valorile corespunzătoare fiecărei înregistrări. \
SRV indică serviciul, portul și protocolul asociat unui serviciu. \
PTR furnizează informații despre serviciul disponibil pe un anumit hostname. \
A indică adresa IP asociată unui serviciu. \
TXT oferă informații adiționale despre serviciu, cum ar fi parametri de configurare sau descrierea serviciului. \
Toate aceste tipuri de înregistrări vor trebui construite, iar pachetele vor fi procesate și trimise către rețea. 

# 3. Monitorizarea resurselor sistemului (procesor, memorie, temperatură)
Pentru a monitoriza resursele sistemului, se poate utiliza librăria psutil, care oferă funcționalități pentru a obține date despre utilizarea procesorului, memoriei și temperaturii dispozitivului.

Pașii de implementare:

Foloim funcțiile psutil pentru a colecta datele necesare, precum utilizarea CPU-ului, utilizarea memoriei sau temperaturile. \
Aceste informații vor fi expuse sub formă de servicii DNS-SD, permițând altor dispozitive să le acceseze prin rețea. 


# 4. Descoperirea serviciilor în rețeaua locală
O alta parte va fi responsabila pentru descoperirea serviciilor disponibile în rețea. Acesta va trimite cereri multicast și va afișa adresele IP și valorile resurselor asociate fiecărei intrări descoperite.

# 5. Implementarea caching-ului
Pentru a reduce cererile repetate de rețea, trebuie implementat un mecanism de caching. Acest cache va stoca datele descoperite pe baza valorilor TTL ale înregistrărilor DNS. Astfel, se vor economisi resurse și timp, evitând cereri inutile.

# 6. Controlul valorii TTL
În partea de monitorizare, voi implementa o opțiune prin care să pot modifica valoarea TTL pentru fiecare resursă în parte. Acest control îmi va permite să gestionez cât timp rămân valide resursele în cache și să optimizez traficul de rețea.


# Resurse utile
Pentru a înțelege mai bine cum implementez aceste concepte,ne vom baza pe următoarele documente și resurse:

[RFC 6762 pentru detalii tehnice despre Multicast DNS (mDNS)](https://datatracker.ietf.org/doc/html/rfc6762) \
[RFC 6763 pentru informații despre DNS-based Service Discovery (DNS-SD)](https://datatracker.ietf.org/doc/html/rfc6763) \
[Documentația pentru socket în Python](https://docs.python.org/3/library/socket.html)
