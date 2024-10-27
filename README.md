#                                                               Implementare mDNS și DNS-SD. Documentație Tehnică 

Introducere:
Acest proiect implementează un sistem de descoperire a serviciilor folosind mDNS (Multicast DNS) și DNS-SD (DNS Service Discovery). Aplicația permite monitorizarea resurselor sistemului și expunerea lor ca servicii în rețeaua locală.

# Introducere:

1. ( _mDNS (Multicast DNS)_ ) este o tehnologie care permite realizarea operațiilor de tip DNS într-o rețea locală mică, fără a necesita un server DNS centralizat. Fiecare dispozitiv din rețea poate obține automat un nume unic de tipul „MyComputer.local”, făcând mai ușoară identificarea și comunicarea între dispozitivele conectate.

# Tipuri de mesaje mDNS
1. Query (Cerere):
Acest mesaj este trimis atunci când un dispozitiv dorește să afle informații despre un alt dispozitiv din rețea. De exemplu, dacă un dispozitiv vrea să cunoască adresa IP asociată unui anumit nume (ex. „MyComputer.local”), va trimite un mesaj de tip query. Query-urile sunt trimise către o adresă de multicast specială (de obicei, 224.0.0.251 pentru IPv4 sau FF02::FB pentru IPv6, 5353 port standard), astfel încât toate dispozitivele din rețea să le poată recepționa.
2. Response (Răspuns):
Atunci când un dispozitiv primește o cerere care îi corespunde, acesta trimite un răspuns mDNS. De exemplu, dacă un dispozitiv a primit o cerere pentru „MyComputer.local” și acesta este numele său, va răspunde cu adresa sa IP. Răspunsurile mDNS includ diferite tipuri de înregistrări DNS, cum ar fi A (pentru adresa IP), PTR (pentru servicii), SRV (pentru informații despre serviciu, port și protocol) și TXT (pentru date suplimentare despre serviciu).

 # 2. DNS-SD (DNS-based Service Discovery) este o metodă prin care dispozitivele dintr-o rețea locală pot fi descoperite și identificate în funcție de serviciile pe care le oferă. Acest lucru permite dispozitivelor să colaboreze fără configurări complexe; de exemplu, un telefon poate trimite comanda de imprimare către o imprimantă din aceeași rețea, datorită faptului că ambele dispozitive se pot recunoaște reciproc și pot comunica direct.

# Cerințe Funcționale:

1.Utilizarea modulului socket pentru comunicație \
2.Implementarea structurii pachetelor mDNS/DNS-SD \
3.Monitorizarea resurselor sistemului (procesor, memorie, temperatură) \
4.Descoperirea serviciilor în rețeaua locală \
5.Implementarea mecanismului de caching \
6.Control TTL pentru monitorizare

# Tipuri de înregistrări DNS utilizate:
SRV: Descrie serviciul, portul și protocolul asociat.
PTR: Indică serviciile disponibile.
A: Înregistrarea adresei IP pentru o anumită gazdă.
TXT: Înregistrări text ce oferă informații suplimentare despre servicii.

# Mediul de dezvoltare și configurarea socket-urilor:
Pentru a implementa mDNS, va trebui să folosim socket-uri pentru a trimite și primi pachete pe adresele multicast. Aceste socket-uri vor folosi protocolul UDP pentru a trimite cereri DNS și a primi răspunsuri. De asemenea, trebuie ca pachetele trimise să respectă structura specifică a mDNS și DNS-SD.

# Mecanisme de caching
Pentru a optimiza aplicația, vom implementa un mecanism de caching. Acest mecanism va stoca rezultatele DNS descoperite pentru o perioadă determinată, bazându-se pe valoarea TTL (Time To Live) a fiecărui pachet. Acest lucru va reduce numărul de cereri de rețea și va îmbunătăți eficiența generală a aplicației.

Pașii de implementare:
# 1. Structurarea pachetelor DNS (SRV, PTR, A)
Mai întâi, trebuie creată o structură de pachete DNS-SD (SRV, PTR, TXT, A) pe care le voi trimite în rețea.

# 2. Monitorizarea resurselor sistemului
Pentru a monitoriza diverse resurse ale sistemului (precum utilizarea procesorului, memoriei și temperatura), vom utiliza un script care utilizează modulele Python potrivite, cum ar fi psutil. Acesta permite preluarea datele despre resursele sistemului și monitorizarea în timp real.

# 3. Expunerea resurselor ca servicii DNS-SD
Crearea unei interfațe care va permite selectarea resurselor pe care vreau să le monitorizez. Apoi, aceste resurse vor fi expuse în rețea sub forma unor înregistrări DNS-SD (SRV). Înregistrările PTR vor fi configurate pentru a arăta către hostname-urile resurselor monitorizate.

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
