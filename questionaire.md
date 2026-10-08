# **UNIVERSAL QUESTIONNAIRE FOR PROJECTS & CODE**

**Use this checklist for EVERY project, feature, and code snippet. 
Ask in order. Same questions = consistent thinking.
THIS WILL GIVE YOU ARCHITECTURAL REASONING**

---

## **LEVEL 1: PROJECT UNDERSTANDING**

### **Before you code anything:**

1. **What problem does this solve?**
   - (Answer in 1 sentence. Why does it exist?)

2. **Who uses it?**
   - (Answer: User type. What do they need?)

3. **What are the constraints?**
   - (Time? Database size? Traffic? Team size?)

4. **How do I measure success?**
   - (List 3 measurable outcomes)

---

## **LEVEL 2: ARCHITECTURE DECISIONS**

### **When designing the system:**

5. **What are my modules/domains?**
   - (List them. What's each responsible for?)

6. **How do modules communicate?**
   - (Interface/API between them? Or direct DB access? CHOOSE: Interface.)

7. **What data does each module own?**
   - (Module X owns tables: ___. Module Y owns tables: ___)

8. **What are the dependencies?**
   - (Module A → Module B → Module C? Draw the flow.)

---

## **LEVEL 3: FEATURE IMPLEMENTATION**

### **When building a feature:**

9. **What is the happy path?**
   - (Step-by-step: Input → Process → Output)

10. **What can go wrong?**
    - (List 3 edge cases. How do I handle each?)

11. **Which layer does each piece live in?**
    - (Domain = business rule? UseCase = orchestration? Adapter = database?)

12. **Can I test this without the full app?**
    - (YES = good design. NO = refactor.)

---

## **LEVEL 4: CODE DESIGN**

### **Before writing a function:**

13. **What is the ONE job of this function?**
    - (1 sentence. If it's 2 jobs, split into 2 functions.)

14. **What goes in? What comes out?**
    - (Input types → Output types. Clear contract?)

15. **Does this function depend on a database/framework?**
    - (YES = belongs in Adapter layer. NO = belongs in Domain/UseCase.)

16. **Can I test this function alone?**
    - (YES = good. NO = inject dependencies.)

---

## **LEVEL 5: CODE QUALITY**

### **After writing code:**

17. **Is this function pure?**
    - (Same input → same output, always? Or does it change state?)

18. **Does this violate any module boundaries?**
    - (Is Customer module calling Lead module's DB directly? FIX IT.)

19. **If I renamed one module, would this break?**
    - (Tight coupling? Loose coupling?)

20. **Can someone else understand this in 2 minutes?**
    - (Good variable names? Comments for why, not what?)

---

## **LEVEL 6: DATABASE DESIGN**

### **When designing tables:**

21. **Is this normalized? (No data duplication?)**
    - (Can I update one place and it updates everywhere? YES = good.)

22. **Do I have foreign keys?**
    - (Referential integrity enforced? YES = safe.)

23. **What indexes do I need?**
    - (Frequently searched fields? Index them.)

24. **Can I write the query without N+1?**
    - (Use JOIN or separate calls? Pick: JOIN = faster.)

---

## **LEVEL 7: API DESIGN**

### **When building REST endpoints:**

25. **Is this resource-oriented?**
    - (GET /users, not /getUsers? Resource nouns, not verbs?)

26. **Am I using the right HTTP method?**
    - (GET = read? POST = create? PATCH = update? DELETE = remove?)

27. **Is my response contract consistent?**
    - (Same format for all endpoints? { "data": ..., "error": null }?)

28. **What errors can happen?**
    - (404 if not found? 400 if invalid input? 500 if server error?)

---

## **LEVEL 8: COMMUNICATION & DOCUMENTATION**

### **When presenting/explaining:**

29. **Can I draw this in 30 seconds?**
    - (Boxes for modules, arrows for data flow. Simple diagram?)

30. **Can I explain the main decision in 1 sentence?**
    - ("I used a hash map instead of a list for O(1) lookup speed.")

31. **What was my alternative? Why didn't I choose it?**
    - (Alternative: ___. Reason I didn't: ___)

32. **If I changed this, what breaks?**
    - (Dependencies? Other modules affected?)

---

## **HOW TO USE THIS**

### **For Each Project:**
```
1. Answer Q1-4 (project scope)
2. Answer Q5-8 (architecture)
3. Answer Q9-12 (each feature)
4. Answer Q13-20 (each function)
5. Answer Q21-24 (database)
6. Answer Q25-28 (API)
7. Answer Q29-32 (communication)
```

### **For Each Code Review:**
```
Ask Q29: Can I draw this in 30 seconds?
Ask Q30: Can I explain the main decision?
Ask Q31: What was my alternative?
Ask Q32: What breaks if I change this?
```

### **For Interview/Presentation:**
```
Ask Q1: What problem does this solve?
Ask Q5: What are my modules?
Ask Q30: What was the main design decision?
Ask Q32: What breaks if I change this?
```

---

## **MEMORY DEVICE: "4-8-12-16-20-24-28-32"**

Memorize the question numbers:

| Level | Qs | Focus |
|---|---|---|
| Project | 1-4 | Why? Who? Constraints? Success? |
| Arch | 5-8 | Modules? Communication? Data? Dependencies? |
| Feature | 9-12 | Path? Errors? Layers? Testable? |
| Code | 13-16 | Job? In/Out? Layer? Independent? |
| DB | 17-20 | Pure? Boundaries? Coupling? Clarity? |
| DB Design | 21-24 | Normalized? FK? Indexes? N+1? |
| API | 25-28 | Resource-oriented? Methods? Contract? Errors? |
| Comm | 29-32 | Drawable? Explainable? Alternative? Impact? |

---

## **WHEN TO STOP ASKING**

✅ When all Q32 checks pass:
- Can draw it
- Can explain it
- Know alternative
- Know what breaks

❌ When stuck on a question:
- Don't move forward
- Fix that layer first

---

**Print this. Bookmark it. Use it for every project, feature, and code snippet for the next 8 weeks. Same questions → consistent thinking → better communication → stronger memory.**